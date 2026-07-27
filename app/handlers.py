from base64 import b64decode
import binascii

from fastapi import HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session

from app.state import DATASETS
from app.state import CHALLENGES
from app.state import CORRECT_RESULTS

from app.models import RunRulePayloadObject, RunRuleReturnObject
from app.models import ValidateRulePayloadObject, VaidateRuleReturnObject
from app.models import ChallengeResponse
from app.models import RunChallengePayloadObject, RunChallengeResponseObject
from app.models import ValidateSigmaRulePayload, ValidateSigmaRuleResponse
from app.models import TranspileRulePayload, TranspileRuleResponse

from app.parser import load_sigma_rule
import app.matcher as MatcherWorker
from app.matcher import event_in_pool

from app.sigma_handler import validate_sigma_rule
from app.sigma_handler import transpile_sigma_rule

from app.db import Challenge
from app.db.session import get_db

def get_log_datasets():
    """\
    Returns a json list of dataset names
    
    Example:
    ```json
    [
        "web_access",
        "sysmon",
        "windows_security"
    ]
    ```
    """
    return list(DATASETS.keys())


def validate_rule(payload: ValidateRulePayloadObject) -> VaidateRuleReturnObject:
    """\
    - `rule`: has to be base64 encoded

    is soft and will return json object
    ```json
    {
        "valid": bool,
        "error": str
    }
    ```
    as long as proper base64 encoded string is given
    """

    rule = payload.rule
    try:
        rule = b64decode(rule).decode("utf-8")
    except (UnicodeDecodeError, binascii.Error, ValueError, TypeError) as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)+ " | send a properly base64 encoded string"
        )

    try:
        load_sigma_rule(rule)
        return VaidateRuleReturnObject(valid=True, error="nil")

    except Exception as e:
        return VaidateRuleReturnObject(valid=False, error=str(e)+" | error in parsing yaml")


def get_challenges_wrapper() -> list[ChallengeResponse] | None:
    """\
    Gives the entire `challenges` table in json.

    Looks like:
    ```jsonc
    [
      {
        "id": 1,
        "title": "title of challenge",
        "question": "Imagine long question here",
        "dataset": "web_access", // hardcoded
        "correct_answer": "base64_encoded_sigma_rule"
      }
    ]
    ```
    """
    return CHALLENGES

def get_challenges_by_id(id: int) -> ChallengeResponse:
    """\
    Gives one row of the challenges table, match `id`

    ```jsonc
    {
      "id": 1,
      "title": "title of challenge",
      "question": "Imagine long question here",
      "dataset": "web_access", // hardcoded
      "correct_answer": "base64_encoded_sigma_rule"
    }
    ```
    """
    for challenge in CHALLENGES:
        if challenge.id == id:
            return challenge
    else:
        raise HTTPException(status_code=404, detail="challenge not found")


def run_rule(payload: RunRulePayloadObject) -> RunRuleReturnObject:
    """\
    Do not directly call from frontend, is used for playground and "correct answer" execution.

    Arbitrary rule execution against provided dataset.

    - `rule`: has to be base64 encoded
    - `dataset`: has to be any of the items returned by `GET /log-datasets`

    is hard and will throw error when rule is not valid
    """
    rule = payload.rule

    try:
        rule = b64decode(rule).decode("utf-8")
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="properly base64 encode it"
        )

    results = MatcherWorker.run_matcher(rule, payload.dataset)

    return RunRuleReturnObject(count=len(results), result=results)


def run_challenge(id: int, payload: RunChallengePayloadObject) -> RunChallengeResponseObject:
    """\
    Executes the given sigma rule for the given challenge (by `id`) and returns output and score.

    `score = ( (true_positive - (false_positive + false_negative)) / total ) * 100`

    Request sample:
    ```json
    {
      "rule": "base64_encoded_string"
    }
    ```

    Response sample:
    ```jsonc
    {
      "score": 0,
      "true_positive": 0,
      "false_positive": 0,
      "false_negative": 0,
      "total": 0,
      "current_result": {...}, // internally called `run_rule`
      "correct_result": {...}, // retrieved from global state, which was loaded from DB at startup
    }
    ```
    """
    current_challenge: Challenge = None
    for challenge in CHALLENGES:
        if challenge.id == id:
            current_challenge = challenge
            break
    else:
        raise HTTPException(status_code=404, detail="challenge not found")


    # CORRECT_RESULT with id is guaranteed to exist since we already ran it against CHALLENGES
    # and CORRECT_RESULTS loads from CHALLENGES
    correct_result: dict = CORRECT_RESULTS[id].result

    total = len(correct_result)

    run_rule_payload = RunRulePayloadObject(rule=payload.rule, dataset=current_challenge.dataset)
    current_run_output: dict = run_rule(run_rule_payload).result



    true_positive = 0
    false_positive = 0
    # true_negative = 0 # not needed
    false_negative = 0

    for event in current_run_output:
        if event_in_pool(event, correct_result):
            true_positive+=1
        else:
            false_positive+=1

    for event in correct_result:
        if not event_in_pool(event, current_run_output):
            false_negative += 1

    score = ((true_positive - (false_positive + false_negative))/total)*100

    return RunChallengeResponseObject(
        score = score,
        true_positive = true_positive,
        false_positive = false_positive,
        false_negative = false_negative,
        total = total,
        current_result = current_run_output,
        correct_result = correct_result
    )

def validate_sigma_rule_handler(payload: ValidateSigmaRulePayload) -> ValidateSigmaRuleResponse:
    """\
    - `rule`: base64 rule, or else error

    is soft and wont throw error when sigma rule is invalid

    Payload:
    ```json
    {
      "rule": "base64_encoded_string"
    }
    ```

    Response:
    ```json
    {
      "valid": true,
      "error": "nil"
    }
    ```
    """
    rule = ""
    try:
        rule = b64decode(payload.rule)
    except (UnicodeDecodeError, binascii.Error, ValueError, TypeError) as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)+ " | send a properly base64 encoded string"
        )
    valid, error = validate_sigma_rule(rule=rule)
    response = ValidateSigmaRuleResponse(valid=valid, error=error)

    return response

def transpile_sigma_rule_handler(payload: TranspileRulePayload) -> TranspileRuleResponse:
    """\
    is hard
    - `rule`: base64 encoded, valid sigma rule, or else error
    - `target`: enum('splunk_sql', 'sentinel_kql') or else error

    Payload:
    ```json
    {
      "rule": "base64_encoded_string",
      "target": "splunk_spl"
    }
    ```

    Response:
    ```json
    {
      "query": "string"
    }
    ```
    """

    rule = ""
    try:
        rule = b64decode(payload.rule)
    except (UnicodeDecodeError, binascii.Error, ValueError, TypeError) as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)+ " | send a properly base64 encoded string"
        )
    queries = None
    response = None
    try:
        queries = transpile_sigma_rule(rule, payload.target)
        response = TranspileRuleResponse(queries=queries, error="nil")
    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail="malformed request | " + str(e)
        )

    return response



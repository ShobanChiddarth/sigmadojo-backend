from fastapi import HTTPException

from app.parser import load_sigma_rule
from app.state import DATASETS

def evaluate_clause(event, clause):
    """\
    - `event`: a single line from the log.ndjson file
    - `selection`: `parser.load_sigma_rule`'s return object's sub object

    Do not call directly. Call from `evaluate_selection`
    """
    field = clause["field"]
    modifier = clause["modifier"]
    expected = clause["value"]

    if field not in event:
        return False

    actual = event[field]

    if modifier == "equals":
        if isinstance(expected, list):
            return actual in expected
        return actual == expected

    elif modifier == "contains":
        if isinstance(expected, list):
            return any(str(x) in str(actual) for x in expected)
        return str(expected) in str(actual)

    elif modifier == "startswith":
        if isinstance(expected, list):
            return any(str(actual).startswith(str(x)) for x in expected)
        return str(actual).startswith(str(expected))

    elif modifier == "endswith":
        if isinstance(expected, list):
            return any(str(actual).endswith(str(x)) for x in expected)
        return str(actual).endswith(str(expected))

    else:
        raise ValueError(f"Unsupported modifier: {modifier}")


def evaluate_selection(event, selection):
    """\
    - `event`: a single line from the log.ndjson file
    - `selection`: `parser.load_sigma_rule`'s return object's sub object

    Do not call directly. Call from `matches`
    """
    for clause in selection["clauses"]:
        if not evaluate_clause(event, clause):
            return False
    return True


def matches(event, matcher):
    """\
    - `event`: a single line from the log.ndjson file
    - `matcher`: return object of `parser.load_sigma_rule`
    """
    condition = matcher["condition"]

    for selection in matcher["detections"]:
        if selection["name"] == condition:
            return evaluate_selection(event, selection)

    return False


def run_matcher(rule_string: str, dataset: str):

    try:
        matcher = load_sigma_rule(rule_string)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    matched = []

    if dataset not in DATASETS:
        raise HTTPException(
            status_code=400,
            detail="Dataset not found"
        )

    for event in DATASETS[dataset]:
        if matches(event, matcher):
            matched.append(event)
    
    return matched


def event_in_pool(event: dict, pool: list[dict]) -> bool:
    for ii in pool:
        if event == ii:
            return True
    else:
        return False

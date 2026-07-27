import os
import sys
import json
import subprocess

from urllib.request import urlretrieve
from pathlib import Path

from app.db.session import SessionLocal
from app.db.loader import load_challenges

from app.state import DATASETS
from app.state import CHALLENGES
from app.state import CORRECT_RESULTS

from app.models import RunRulePayloadObject

from app.handlers import run_rule

log_datasets_path = os.environ.get("LOG_DATASETS_PATH")

def load_ndjson(filepath: str) -> list[dict]:
    result = []

    with open(filepath, "r", encoding="utf-8", newline="\n") as fh:
        for line_num, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                result.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"{filepath}:{line_num}: {e}\n"
                    f"Line: {line}"
                ) from e

    return result

def load_datasets(target: str) -> dict:
    result = {}

    for root, dirs, files in os.walk(target):

        for file in files:
            if not file.endswith(".ndjson"):
                continue
            # os.path.basename('/full/path/file.ndjson') =  'file.ndjson'
            # os.path.splittext('file.ndjson') = ('file', '.ndjson')
            key = os.path.splitext(os.path.basename(file))[0]

            result[key] = load_ndjson(os.path.join(root, file))

        break

    return result


def initialize_datasets():
    if not os.path.exists(log_datasets_path):
        os.mkdir(log_datasets_path)

    logfile_urls = []
    if not os.listdir(log_datasets_path):
        # if nothing is in the folder, download each file from the env var `LOGFILES`
        logfile_urls =  json.loads(
            os.environ.get("LOGFILES", 
                            default='["https://github.com/EdgeRunners-BrewingSec/log-datasets/releases/download/v1.0.0/sysmon.ndjson", "https://github.com/EdgeRunners-BrewingSec/log-datasets/releases/download/v1.0.0/web_access.ndjson", "https://github.com/EdgeRunners-BrewingSec/log-datasets/releases/download/v1.0.0/windows_security.ndjson"]'
                        )
        )

    for link in logfile_urls:
        filename = link.split("/")[-1]
        urlretrieve(link, Path(log_datasets_path) / filename)


    if not os.listdir(log_datasets_path):
        raise Exception("log dataset folder empty and link is also empty")
        sys.exit()

    DATASETS.update(load_datasets(log_datasets_path))

def initialize_challenges():
    db = SessionLocal()

    try:
        CHALLENGES.extend(
            load_challenges(db)
        )

        for challenge in CHALLENGES:

            payload = RunRulePayloadObject(rule=challenge.correct_answer, dataset=challenge.dataset)
            result = run_rule(payload)

            CORRECT_RESULTS[challenge.id] = result

    finally:
        db.close()

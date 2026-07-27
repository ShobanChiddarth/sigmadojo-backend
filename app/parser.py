"""\
Standalone module
"""

import yaml

def parse_detection(selection_name, selection):
    clauses = []

    for key, value in selection.items():
        if "|" in key:
            field, modifier = key.split("|", 1)
        else:
            field = key
            modifier = "equals"

        clauses.append(
            {
                "field": field,
                "modifier": modifier,
                "value": value,
            }
        )

    return {
        "name": selection_name,
        "clauses": clauses,
    }

def load_sigma_rule(rule: str):
    rule = yaml.safe_load(rule)

    matcher = {
        "title": rule.get("title"),
        "condition": rule["detection"]["condition"],
        "detections": [],
    }

    for name, selection in rule["detection"].items():
        if name == "condition":
            continue

        matcher["detections"].append(parse_detection(name, selection))

    return matcher

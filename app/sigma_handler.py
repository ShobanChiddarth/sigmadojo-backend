from sigma.collection import SigmaCollection
from sigma.exceptions import SigmaError
from sigma.backends.splunk import SplunkBackend
from sigma.backends.microsoft365defender import KustoBackend as SentinelBackend

def validate_sigma_rule(rule: str) -> tuple[bool, str | None]:
    """\
    `rule` must be multi line yaml string
    """
    try:
        SigmaCollection.from_yaml(rule)
        return True, "nil"
    except SigmaError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def transpile_sigma_rule(rule: str, target: str) -> list[str]:
    """\
    - `rule` must be multi line yaml string, valid sigma rule, single rule
    - `target` must be either `splunk_spl` or `sentinel_kql`
    """

    if target not in ("splunk_spl", "sentinel_kql"):
        raise ValueError("target must be `splunk_spl` or `sentinel_kql")
    
    sigma_collection = SigmaCollection.from_yaml(rule)

    backend = None
    if target=="splunk_spl":
        backend = SplunkBackend()
    elif target=="sentinel_kql":
        backend = SentinelBackend()
    
    queries = backend.convert_rule(next(iter(sigma_collection.rules)))

    return queries


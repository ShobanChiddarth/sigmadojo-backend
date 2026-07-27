from fastapi import APIRouter

from app.handlers import validate_rule
from app.handlers import get_log_datasets
from app.handlers import get_challenges_wrapper
from app.handlers import get_challenges_by_id
from app.handlers import run_rule
from app.handlers import run_challenge
from app.handlers import validate_sigma_rule_handler
from app.handlers import transpile_sigma_rule_handler

router = APIRouter()

router.add_api_route(
    "/log-datasets",
    get_log_datasets,
    methods=["GET"],
)

router.add_api_route(
    "/validate-rule",
    validate_rule,
    methods=["POST"],
)

router.add_api_route(
    "/run-rule",
    run_rule,
    methods=["POST"]
)

router.add_api_route(
    "/challenges",
    get_challenges_wrapper,
    methods=["GET"],
)

router.add_api_route(
    "/challenges/{id}",
    get_challenges_by_id,
    methods=["GET"]
)

router.add_api_route(
    "/challenges/{id}",
    run_challenge,
    methods=["POST"],
)

router.add_api_route(
    "/validate-sigma-rule",
    validate_sigma_rule_handler,
    methods=["POST"]
)


router.add_api_route(
    "/transpile-rule",
    transpile_sigma_rule_handler,
    methods=["POST"],
)

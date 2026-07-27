from pydantic import BaseModel, Field

class RunChallengePayloadObject(BaseModel):
    """\
    - `rule`: base64 encoded string
    """
    rule: str = Field(
        example="base64_encoded_string"
    )

class RunChallengeResponseObject(BaseModel):
    score: float
    true_positive: int
    false_positive: int
    false_negative: int
    total: int
    current_result: list[dict]
    correct_result: list[dict]

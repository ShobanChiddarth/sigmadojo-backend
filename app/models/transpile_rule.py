from pydantic import BaseModel, Field

class TranspileRulePayload(BaseModel):
    rule: str = Field(
        example="base64_encoded_string"
    )
    target: str = Field(
        example="splunk_spl|sentinel_kql"
    )

class TranspileRuleResponse(BaseModel):
    queries: list[str]
    error: str

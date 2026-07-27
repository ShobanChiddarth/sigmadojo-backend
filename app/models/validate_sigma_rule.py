from pydantic import BaseModel, Field

class ValidateSigmaRulePayload(BaseModel):
    rule: str = Field(
        example="base64_encoded_string"
    )

class ValidateSigmaRuleResponse(BaseModel):
    valid: bool
    error: str

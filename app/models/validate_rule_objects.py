from pydantic import BaseModel, Field

class ValidateRulePayloadObject(BaseModel):
    rule: str = Field(
        example="base64encoded_string"
    )

class VaidateRuleReturnObject(BaseModel):
    valid: bool
    error: str


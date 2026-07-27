from pydantic import BaseModel, Field


class RunRulePayloadObject(BaseModel):
    rule: str = Field(
        example="base64encoded_string"
    )
    dataset: str = Field(
        example="sysmon/windows_security/web_access"
    )

class RunRuleReturnObject(BaseModel):
    count: int = Field(
        example="number of `result`"
    )
    result: list[dict] = Field(
        example="list of filtered `events` in .ndjson files"
    )

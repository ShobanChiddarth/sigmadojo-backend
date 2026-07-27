from pydantic import BaseModel, ConfigDict

class ChallengeResponse(BaseModel):
    """ORM model for challenge metadata.

    Fields:
    - id: integer primary key
    - title: short human-readable title
    - question: textual description of the challenge
    - dataset: dataset identifier/path used by the challenge
    - correct_answer: stored as text (base64)
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    question: str
    dataset: str
    correct_answer: str

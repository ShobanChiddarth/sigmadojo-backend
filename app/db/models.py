from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Challenge(Base):
    """ORM model for challenge metadata.

    Fields:
    - id: integer primary key
    - title: short human-readable title
    - question: textual description of the challenge
    - dataset: dataset identifier/path used by the challenge
    - correct_answer: stored as text (base64)
    """

    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    question = Column(Text, nullable=True)
    dataset = Column(String(255), nullable=False)
    correct_answer = Column(Text, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - simple helper
        return f"<Challenge id={self.id!r} title={self.title!r}>"

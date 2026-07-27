"""\
Loads every record from model `challenges` into `app.state:CHALLENGES`
"""
from sqlalchemy.orm import Session

from app.db.models import Challenge


def load_challenges(db: Session) -> dict:
    challenges = []

    rows = db.query(Challenge).all()

    for challenge in rows:
        challenges.append(challenge)

    return challenges

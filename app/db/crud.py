
from sqlalchemy.orm import Session

from app.db.models import Challenge

def get_challenges(db: Session) -> list[Challenge] | None:
    return db.query(Challenge).all()

# def get_challenge(db: Session, challenge_id: int) -> Challenge | None:
#     return (
#         db.query(Challenge)
#         .filter(Challenge.id == challenge_id)
#         .first()
#     )

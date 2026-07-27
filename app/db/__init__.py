from app.db.database import engine
from app.db.models import Base
from app.db.models import Challenge
from app.db.seeder import seed_database

def initialize_database():
    # if it does not exist, create
    # else, do nothing
    Base.metadata.create_all(bind=engine)

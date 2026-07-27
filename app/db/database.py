import os

from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///./sigmadojo.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

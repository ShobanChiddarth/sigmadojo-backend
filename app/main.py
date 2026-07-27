import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from app.routes import router
from app.startup import initialize_datasets
from app.startup import initialize_challenges

from app.db import initialize_database
from app.db import seed_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    seed_database()

    initialize_datasets()
    initialize_challenges()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        os.environ.get("FRONTEND", "http://localhost:3001")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

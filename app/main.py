import os
from contextlib import asynccontextmanager

import logfire
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.data import init_db
from app.routes import family_router, recipe_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    lifespan=lifespan,
    swagger_ui_init_oauth={"clientId": os.environ.get("AUTH0_CLIENT_ID")},
)

logfire.configure()
logfire.instrument_fastapi(app)

app.include_router(family_router)
app.include_router(recipe_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

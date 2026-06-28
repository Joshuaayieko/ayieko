"""Orbes backend application entrypoint."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .routers import auth, chat, memory, tools, vision
from .seed import seed_admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orbes")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_admin()
    logger.info("Orbes backend ready (env=%s, llm=%s)", settings.orbes_env, settings.orbes_llm_model)
    yield


app = FastAPI(
    title="Orbes AI Assistant",
    description="Backend for the Orbes multi-modal, multi-agent AI assistant.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — tighten allow_origins for production deployments.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(memory.router)
app.include_router(tools.router)
app.include_router(vision.router)


@app.get("/")
def root():
    return {
        "name": "Orbes",
        "version": "0.1.0",
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}

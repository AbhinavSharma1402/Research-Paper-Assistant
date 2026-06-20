import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.logging import configure_logging, logger
from backend.db.base import init_db
from backend.routes import auth, chat, docs, users
from backend.utils.exceptions import http_exception_handler


def create_application() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title=settings.app_name,
        description="Production-ready research paper assistant API with persistent chat, JWT auth, and RAG search.",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix=settings.api_prefix)
    app.include_router(users.router, prefix=settings.api_prefix)
    app.include_router(docs.router, prefix=settings.api_prefix)
    app.include_router(chat.router, prefix=settings.api_prefix)

    app.add_exception_handler(Exception, http_exception_handler)

    return app


app = create_application()


@app.on_event("startup")
def startup_event():
    logger.info("Starting %s", settings.app_name)
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.vector_store_root, exist_ok=True)
    init_db()

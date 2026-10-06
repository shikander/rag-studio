"""FastAPI entry point. Run with: uvicorn rag_studio.api.main:app --reload"""
from fastapi import FastAPI

from rag_studio.api.error_handlers import register_error_handlers
from rag_studio.api.routes import health, runs


def create_app() -> FastAPI:
    app = FastAPI(title="RAG Studio API", version="0.1.0")
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(runs.router)
    return app


app = create_app()
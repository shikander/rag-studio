from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from rag_studio.domain.errors import NoCriteriaFoundError, RunNotFoundError


def _json_error(status_code: int, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(NoCriteriaFoundError)
    async def no_criteria(_: Request, exc: NoCriteriaFoundError) -> JSONResponse:
        return _json_error(422, exc)

    @app.exception_handler(RunNotFoundError)
    async def run_not_found(_: Request, exc: RunNotFoundError) -> JSONResponse:
        return _json_error(404, exc)
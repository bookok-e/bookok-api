from typing import Literal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

Source = Literal["data4library", "yes24", "embedding", "llm"]


class UpstreamUnavailable(Exception):
    """외부 API 실패. 대체할지 503으로 끝낼지는 각 기능의 service.py가 정한다."""

    def __init__(self, source: Source, detail: str = ""):
        super().__init__(f"{source}: {detail}" if detail else source)
        self.source = source


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def invalid_input(_: Request, exc: RequestValidationError) -> JSONResponse:
        loc = exc.errors()[0]["loc"] if exc.errors() else ()
        field = next((str(p) for p in reversed(loc) if isinstance(p, str)), None)
        return JSONResponse(status_code=400, content={"error": "invalid_input", "field": field})

    @app.exception_handler(UpstreamUnavailable)
    async def upstream(_: Request, exc: UpstreamUnavailable) -> JSONResponse:
        return JSONResponse(status_code=503, content={"error": "upstream_unavailable"})

# app/middlewares/middleware.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class ErrorHandler(BaseHTTPMiddleware):
    """
    Middleware class to handle and format errors that occur within the application.
    """

    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response | JSONResponse:
        try:
            return await call_next(request)
        except Exception as e:
            response = {
                "error_trace": str(e),
            }

            return JSONResponse(status_code=500, content=response)

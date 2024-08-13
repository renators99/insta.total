# health.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse

health_router = APIRouter()


@health_router.get("/ping")
async def health_check() -> JSONResponse:
    """
    health check
    """
    return JSONResponse({"message": "pong"})

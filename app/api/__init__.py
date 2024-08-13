# app/api/__init__.py

from fastapi import APIRouter

from app.api.health import health_router
from app.api.metahashtags import router as metahashtags_router
from app.api.insta_profile_generator import router as insta_profile_generator_router

routers = APIRouter()
routers.include_router(health_router)
routers.include_router(metahashtags_router, prefix="/metahashtags", tags=["MetaHashtags"])
routers.include_router(insta_profile_generator_router, prefix="/insta_profile_generator", tags=["Insta Profile Generator"])

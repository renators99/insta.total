from fastapi import FastAPI
from app.middlewares.middleware import ErrorHandler
from app.api.health import health_router
from app.api.metahashtags import router as metahashtags_router
from app.api.insta_profile_generator import router as insta_profile_generator_router


app = FastAPI()
app.include_router(health_router)
app.include_router(metahashtags_router)
app.include_router(insta_profile_generator_router)
app.add_middleware(ErrorHandler)


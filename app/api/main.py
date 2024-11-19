from fastapi import APIRouter

from app.api.routes import ai, login

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(ai.router, tags=["assistant"])

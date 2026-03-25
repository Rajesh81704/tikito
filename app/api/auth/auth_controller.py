from fastapi import APIRouter
from app.api.auth import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login(data: dict):
    return auth_service.login(data)

@router.post("/logout")
def logout(data: dict):
    return auth_service.logout(data)

@router.post("/refresh")
def refresh(data: dict):
    return auth_service.refresh_token(data)

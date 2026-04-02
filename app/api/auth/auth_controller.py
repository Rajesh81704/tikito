from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.auth import auth_service
from app.api.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginSchema(BaseModel):
    identifier: str  # phone or email
    password: str
    role: str  # "user" | "admin" | "vendor"

@router.post("/login")
def login(data: LoginSchema):
    return auth_service.login(data.model_dump())

@router.post("/logout")
def logout():
    return auth_service.logout()

@router.post("/refresh")
def refresh(data: dict):
    return auth_service.refresh_token(data)

@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user

@router.get("/test-auth")
def test_auth(current_user: dict = Depends(get_current_user)):
    return {"authenticated": True, "user": current_user}



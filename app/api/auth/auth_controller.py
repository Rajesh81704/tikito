from fastapi import APIRouter, Depends
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.api.auth import auth_service
from app.api.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginSchema(BaseModel):
    identifier: str  
    password: str
    role: str  

class UserMeSchema(BaseModel):
    user_id: UUID
    full_name: str
    phone_no: str
    email: str | None = None
    is_active: bool
    is_verified: bool
    created_at: datetime

class VendorMeSchema(BaseModel):
    vendor_id: UUID
    vendor_full_name: str
    vendor_phone_no: str | None = None
    vendor_email_id: str | None = None
    vendor_address: str | None = None
    is_active: bool
    created_at: datetime

class AdminMeSchema(BaseModel):
    admin_id: UUID
    full_name: str
    email: str
    phone_no: str | None = None
    role: str | None = None
    is_active: bool
    created_at: datetime

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
    return auth_service.get_me(current_user)

@router.get("/test-auth")
def test_auth(current_user: dict = Depends(get_current_user)):
    return {"authenticated": True, "user": current_user}



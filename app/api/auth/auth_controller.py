from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.api.auth import auth_service
from app.api.auth import password_service
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
def logout(current_user: dict = Depends(get_current_user)):
    return auth_service.logout()

@router.post("/refresh")
def refresh(data: dict, current_user: dict = Depends(get_current_user)):
    return auth_service.refresh_token(data)

@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return auth_service.get_me(current_user)

@router.get("/test-auth")
def test_auth(current_user: dict = Depends(get_current_user)):
    return {"authenticated": True, "user": current_user}


# --- Forgot Password Flow ---

class ForgotPasswordSchema(BaseModel):
    email: str
    role: str  # "user", "vendor", or "admin"

class VerifyOtpSchema(BaseModel):
    email: str
    otp: str

class ResetPasswordSchema(BaseModel):
    email: str
    new_password: str

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordSchema):
    return password_service.forgot_password(data.email, data.role)

@router.post("/verify-otp")
def verify_otp(data: VerifyOtpSchema):
    try:
        return password_service.verify_otp(data.email, data.otp)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reset-password")
def reset_password(data: ResetPasswordSchema):
    try:
        return password_service.reset_password(data.email, data.new_password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



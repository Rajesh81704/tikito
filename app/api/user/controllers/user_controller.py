from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.user.services import user_service
from app.api.core.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

class CreateUser(BaseModel):
    full_name: str
    phone_no: str
    email: str | None = None
    password: str

@router.post("/sign-up", status_code=201)
def sign_up(data: CreateUser):
    return user_service.create(data.model_dump())

@router.get("/nearby-turfs")
def get_nearby_turfs(lat: float, lng: float, radius_km: float = 10, current_user: dict = Depends(get_current_user)):
    return user_service.get_nearby_turfs(lat, lng, radius_km)

@router.get("/turfs")
def get_turfs_by_city(city: str, current_user: dict = Depends(get_current_user)):
    return user_service.get_turfs_by_city(city)


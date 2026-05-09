from uuid import UUID
from decimal import Decimal
from datetime import datetime, time, date
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.user.services import user_service
from app.api.user.services import payment_service
from app.api.vendor.services import vendor_service
from app.api.core.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

class CreateUser(BaseModel):
    full_name: str
    phone_no: str
    email: str | None = None
    password: str

class TurfResponseSchema(BaseModel):
    turf_field_id: str
    turf_name: str
    turf_location: str | None = None
    turf_address: str | None = None
    no_of_grounds: int | None = None
    turf_facilities: str | None = None
    turf_rules: str | None = None
    longitude: str | None = None
    latitude: str | None = None

class SlotResponseSchema(BaseModel):
    slot_id: UUID
    day_of_week: str
    start_time: time
    end_time: time
    price: Decimal
    is_peak: bool

class GroundResponseSchema(BaseModel):
    turf_ground_id: UUID
    ground_name: str
    ground_loc: str | None = None
    ground_type: str | None = None
    turf_field_id: UUID
    created_at: datetime
    updated_at: datetime
    ground_images: list[str] | None = None
    is_active: bool | None = None
    slots: list[SlotResponseSchema] = []


class BookSlotSchema(BaseModel):
    slot_id: str

@router.post("/sign-up", status_code=201)
def sign_up(data: CreateUser):
    return user_service.create(data.model_dump())

@router.get("/nearby-turfs")
def get_nearby_turfs(lat: float, lng: float, radius_km: float = 10, current_user: dict = Depends(get_current_user)):
    return user_service.get_nearby_turfs(lat, lng, radius_km)

@router.get("/turfs", response_model=list[TurfResponseSchema])
def get_turfs_by_city(city: str, current_user: dict = Depends(get_current_user)):
    return user_service.get_turfs_by_city(city)

@router.get("/ground-details", response_model=list[GroundResponseSchema])
def get_turf_ground_details(turf_id: str, current_user: dict = Depends(get_current_user)):
    return vendor_service.get_grounds_by_turf(turf_id)

@router.get("/available-slots/{turf_ground_id}")
def get_available_slots(turf_ground_id: str, current_user: dict = Depends(get_current_user)):
    return user_service.get_available_slots(turf_ground_id)

class VerifyPaymentSchema(BaseModel):
    booking_id: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

@router.post("/book", status_code=201)
def book_slot(data: BookSlotSchema, current_user: dict = Depends(get_current_user)):
    return user_service.book_slot(data.model_dump(), current_user)

@router.post("/payment/create-order")
def create_payment_order(booking_id: str, current_user: dict = Depends(get_current_user)):
    return payment_service.create_order(booking_id)

@router.post("/payment/verify")
def verify_payment(data: VerifyPaymentSchema, current_user: dict = Depends(get_current_user)):
    return payment_service.verify_payment(data.model_dump())

@router.get("/my-bookings")
def get_my_bookings(current_user: dict = Depends(get_current_user)):
    return user_service.get_my_bookings(current_user)

@router.delete("/me", status_code=200)
def delete_user(current_user: dict = Depends(get_current_user)):
    return user_service.soft_delete_user(current_user)

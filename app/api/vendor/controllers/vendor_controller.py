from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.vendor.services import vendor_service, vendor_auth_service
from app.api.core.dependencies import get_current_user

router = APIRouter(prefix="/vendors", tags=["vendors"])

class VendorSignupSchema(BaseModel):
    vendor_full_name: str
    vendor_phone_no: str
    vendor_email_id: str | None = None
    vendor_address: str | None = None
    password: str


@router.post("/signup", status_code=201)
def signup(data: VendorSignupSchema):
    return vendor_auth_service.signup(data.model_dump())

class AddTurfSchema(BaseModel):
    turf_name: str
    turf_location: str | None = None
    turf_address: str | None = None
    no_of_grounds: int | None = None
    turf_facilities: str | None = None
    turf_rules: str | None = None
    vendor_id: str
    turf_images:list[str] | None = None

@router.post("/add-turf", status_code=201)
def add_turf(data: AddTurfSchema, current_user: dict = Depends(get_current_user)):
    return vendor_service.add_turf(data.model_dump(), current_user)

from decimal import Decimal
from datetime import time
from enum import Enum

class DayOfWeek(str, Enum):
    SUNDAY = "SUNDAY"
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"

class SlotSchema(BaseModel):
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    price: Decimal
    is_peak: bool = False

class AddGroundSchema(BaseModel):
    ground_name: str
    ground_loc: str | None = None
    ground_type: str | None = None
    turf_field_id: str
    slots: list[SlotSchema] = []

@router.post("/add-ground", status_code=201)
def add_ground(data: AddGroundSchema, current_user: dict = Depends(get_current_user)):
    return vendor_service.add_ground(data.model_dump(), current_user)



from uuid import UUID
from decimal import Decimal
from datetime import datetime, time
from enum import Enum
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

class AddTurfSchema(BaseModel):
    turf_name: str
    turf_location: str | None = None
    turf_address: str | None = None
    no_of_grounds: int | None = None
    turf_facilities: str | None = None
    turf_rules: str | None = None
    turf_images: list[str] | None = None

class EditTurfSchema(BaseModel):
    turf_name: str | None = None
    turf_location: str | None = None
    turf_address: str | None = None
    no_of_grounds: int | None = None
    turf_facilities: str | None = None
    turf_rules: str | None = None

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

class EditGroundSchema(BaseModel):
    ground_name: str | None = None
    ground_loc: str | None = None
    ground_type: str | None = None
    slots: list[SlotSchema] | None = None

class TurfResponseSchema(BaseModel):
    turf_field_id: UUID
    turf_name: str
    turf_location: str | None = None
    turf_address: str | None = None
    no_of_grounds: int | None = None
    vendor_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    turf_facilities: str | None = None
    turf_rules: str | None = None
    turf_images: list[str] | None = None

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

@router.post("/signup", status_code=201)
def signup(data: VendorSignupSchema):
    return vendor_auth_service.signup(data.model_dump())

@router.post("/add-turf", status_code=201)
def add_turf(data: AddTurfSchema, current_user: dict = Depends(get_current_user)):
    return vendor_service.add_turf(data.model_dump(), current_user)

@router.put("/edit-turf/{turf_field_id}")
def edit_turf(turf_field_id: str,  data: EditTurfSchema, current_user: dict = Depends(get_current_user)):
    return vendor_service.edit_turf(turf_field_id, data.model_dump(exclude_none=True), current_user)

@router.post("/add-ground", status_code=201)
def add_ground(data: AddGroundSchema, current_user: dict = Depends(get_current_user)):
    return vendor_service.add_ground(data.model_dump(), current_user)

@router.put("/edit-ground/{turf_ground_id}")
def edit_ground(turf_ground_id: str, data: EditGroundSchema, current_user: dict = Depends(get_current_user)):
    return vendor_service.edit_ground(turf_ground_id, data.model_dump(exclude_none=True), current_user)

@router.get("/my-turfs", response_model=list[TurfResponseSchema])
def get_my_turfs(current_user: dict = Depends(get_current_user)):
    return vendor_service.get_turfs_by_vendor(current_user)

@router.get("/turf/{turf_field_id}/grounds", response_model=list[GroundResponseSchema])
def get_grounds_by_turf(turf_field_id: str, current_user: dict = Depends(get_current_user)):
    return vendor_service.get_grounds_by_turf(turf_field_id)

@router.get("/turf/{turf_field_id}/location")
def get_turf_location(turf_field_id: str):
    return vendor_service.get_turf_location(turf_field_id)

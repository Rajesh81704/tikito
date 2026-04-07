from uuid import UUID
from decimal import Decimal
from datetime import datetime, time, date
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
    turf_images: str | None = None
    is_active: bool | None = None
    latitude: float | None = None
    longitude: float | None = None

class EditTurfSchema(BaseModel):
    turf_name: str | None = None
    turf_location: str | None = None
    turf_address: str | None = None
    no_of_grounds: int | None = None
    turf_facilities: str | None = None
    turf_rules: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class DayOfWeek(str, Enum):
    SUNDAY = "SUNDAY"
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"

class TimeSlotSchema(BaseModel):
    start_time: time
    end_time: time
    price: Decimal
    is_peak: bool = False

class DaySlotSchema(BaseModel):
    day_of_week: DayOfWeek
    slots: list[TimeSlotSchema]

class AddGroundSchema(BaseModel):
    ground_name: str
    ground_loc: str | None = None
    ground_type: str | None = None
    booking_weeks: int = 1

class GroundBookingScheduleSchema(BaseModel):
    turf_ground_id: str
    schedule: list[DaySlotSchema]

class EditGroundSchema(BaseModel):
    ground_name: str | None = None
    ground_loc: str | None = None
    ground_type: str | None = None
    booking_weeks: int | None = None
    schedule: list[DaySlotSchema] | None = None
    ground_images: str | None = None

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

class BookingResponseSchema(BaseModel):
    booking_id: UUID
    booking_date: date
    booking_status: str
    is_available: bool
    booked_at: datetime
    start_time: time
    end_time: time
    price: Decimal
    day_of_week: str
    ground_name: str
    ground_type: str | None = None
    turf_name: str
    turf_address: str | None = None

@router.post("/signup", status_code=201) 
async def signup(data: VendorSignupSchema):
    return vendor_auth_service.signup(data.model_dump())

@router.post("/add-turf", status_code=201)
async def add_turf(data: AddTurfSchema, current_user: dict = Depends(get_current_user)):
    return vendor_service.add_turf(data.model_dump(), current_user)

@router.put("/edit-turf/{turf_field_id}")
async def edit_turf(turf_field_id: str,  data: EditTurfSchema, current_user: dict = Depends(get_current_user)):
    return vendor_service.edit_turf(turf_field_id, data.model_dump(exclude_none=True), current_user)

@router.post("/turf/{turf_field_id}/add-ground", status_code=201)
async def add_ground(turf_field_id: str, data: AddGroundSchema, current_user: dict = Depends(get_current_user)):
    return vendor_service.add_ground(turf_field_id, data.model_dump(), current_user)

@router.put("/edit-ground/{turf_ground_id}")
async def edit_ground(turf_ground_id: str, data: EditGroundSchema, current_user: dict = Depends(get_current_user)):
    return vendor_service.edit_ground(turf_ground_id, data.model_dump(exclude_none=True), current_user)

@router.post("/ground-booking-schedule", status_code=201)
async def set_ground_booking_schedule(data: GroundBookingScheduleSchema, current_user: dict = Depends(get_current_user)):
    return vendor_service.set_ground_booking_schedule(data.model_dump())

@router.put("/ground-booking-schedule/{turf_ground_id}")
async def update_ground_booking_schedule(turf_ground_id: str, data: list[DaySlotSchema], current_user: dict = Depends(get_current_user)):
    return vendor_service.update_ground_schedule(turf_ground_id, [s.model_dump() for s in data])

@router.get("/my-turfs", response_model=list[TurfResponseSchema])
async def get_my_turfs(current_user: dict = Depends(get_current_user)):
    return vendor_service.get_turfs_by_vendor(current_user)

@router.get("/turf/{turf_field_id}/grounds", response_model=list[GroundResponseSchema])
async def get_grounds_by_turf(turf_field_id: str, current_user: dict = Depends(get_current_user)):
    return vendor_service.get_grounds_by_turf(turf_field_id)

@router.get("/turf/{turf_field_id}/location")
async def get_turf_location(turf_field_id: str):
    return vendor_service.get_turf_location(turf_field_id)

@router.get("/bookings", response_model=list[BookingResponseSchema])
async def get_vendor_bookings(current_user: dict = Depends(get_current_user)):
    return vendor_service.get_vendor_bookings(current_user)

class VendorDashboardSchema(BaseModel):
    total_bookings: int
    confirmed_bookings: int
    cancelled_bookings: int
    total_earnings: Decimal
    total_turfs: int
    total_grounds: int

@router.get("/dashboard", response_model=VendorDashboardSchema)
async def get_vendor_dashboard(current_user: dict = Depends(get_current_user)):
    return vendor_service.get_vendor_dashboard(current_user)

@router.put("/bookings/{booking_id}/cancel")
async def cancel_booking(booking_id: str, current_user: dict = Depends(get_current_user)):
    return vendor_service.cancel_booking(booking_id, current_user)


from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.api.admin.services import admin_service
from app.api.core.dependencies import get_current_admin

router = APIRouter(prefix="/admin", tags=["admin"])


class ToggleStatusSchema(BaseModel):
    is_active: bool


# ─── Dashboard ────────────────────────────────────────────────────────────────

@router.get("/dashboard")
def dashboard(current_admin: dict = Depends(get_current_admin)):
    return admin_service.get_dashboard()


# ─── User Management ─────────────────────────────────────────────────────────

@router.get("/users")
def get_all_users(current_admin: dict = Depends(get_current_admin)):
    return admin_service.get_all_users()


@router.get("/users/{user_id}")
def get_user(user_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        return admin_service.get_user_by_id(user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/users/{user_id}/status")
def toggle_user_status(user_id: str, data: ToggleStatusSchema, current_admin: dict = Depends(get_current_admin)):
    try:
        return admin_service.toggle_user_status(user_id, data.is_active)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/users/{user_id}")
def delete_user(user_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        return admin_service.delete_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─── Vendor Management ───────────────────────────────────────────────────────

@router.get("/vendors")
def get_all_vendors(current_admin: dict = Depends(get_current_admin)):
    return admin_service.get_all_vendors()


@router.get("/vendors/{vendor_id}")
def get_vendor(vendor_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        return admin_service.get_vendor_by_id(vendor_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/vendors/{vendor_id}/verify")
def verify_vendor(vendor_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        return admin_service.verify_vendor(vendor_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/vendors/{vendor_id}/status")
def toggle_vendor_status(vendor_id: str, data: ToggleStatusSchema, current_admin: dict = Depends(get_current_admin)):
    try:
        return admin_service.toggle_vendor_status(vendor_id, data.is_active)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/vendors/{vendor_id}")
def delete_vendor(vendor_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        return admin_service.delete_vendor(vendor_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─── Turf Management ─────────────────────────────────────────────────────────

@router.get("/turfs")
def get_all_turfs(current_admin: dict = Depends(get_current_admin)):
    return admin_service.get_all_turfs()


@router.put("/turfs/{turf_field_id}/status")
def toggle_turf_status(turf_field_id: str, data: ToggleStatusSchema, current_admin: dict = Depends(get_current_admin)):
    try:
        return admin_service.toggle_turf_status(turf_field_id, data.is_active)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/turfs/{turf_field_id}")
def delete_turf(turf_field_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        return admin_service.delete_turf(turf_field_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─── Booking Management ──────────────────────────────────────────────────────

@router.get("/bookings")
def get_all_bookings(current_admin: dict = Depends(get_current_admin)):
    return admin_service.get_all_bookings()


@router.put("/bookings/{booking_id}/cancel")
def cancel_booking(booking_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        return admin_service.cancel_booking(booking_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/bookings/{booking_id}")
def delete_booking(booking_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        return admin_service.delete_booking(booking_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

from fastapi import APIRouter
from app.api.vendor.services import vendor_service, vendor_auth_service

router = APIRouter(prefix="/vendors", tags=["vendors"])

@router.post("/signup", status_code=201)
def signup(data: dict):
    return vendor_auth_service.signup(data)

@router.get("/")
def get_all():
    return vendor_service.get_all()

@router.get("/{vendor_id}")
def get_by_id(vendor_id: int):
    return vendor_service.get_by_id(vendor_id)

@router.post("/", status_code=201)
def create(data: dict):
    return vendor_service.create(data)

@router.put("/{vendor_id}")
def update(vendor_id: int, data: dict):
    return vendor_service.update(vendor_id, data)

@router.delete("/{vendor_id}", status_code=204)
def delete(vendor_id: int):
    return vendor_service.delete(vendor_id)

from fastapi import APIRouter
from app.api.admin.services import admin_service

router = APIRouter(prefix="/admins", tags=["admins"])

@router.get("/")
def get_all():
    return admin_service.get_all()

@router.get("/{admin_id}")
def get_by_id(admin_id: int):
    return admin_service.get_by_id(admin_id)

@router.post("/", status_code=201)
def create(data: dict):
    return admin_service.create(data)

@router.put("/{admin_id}")
def update(admin_id: int, data: dict):
    return admin_service.update(admin_id, data)

@router.delete("/{admin_id}", status_code=204)
def delete(admin_id: int):
    return admin_service.delete(admin_id)

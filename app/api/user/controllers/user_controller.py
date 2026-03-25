from fastapi import APIRouter
from app.api.user.services import user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
def get_all():
    return user_service.get_all()

@router.get("/{user_id}")
def get_by_id(user_id: int):
    return user_service.get_by_id(user_id)

@router.post("/", status_code=201)
def create(data: dict):
    return user_service.create(data)

@router.put("/{user_id}")
def update(user_id: int, data: dict):
    return user_service.update(user_id, data)

@router.delete("/{user_id}", status_code=204)
def delete(user_id: int):
    return user_service.delete(user_id)

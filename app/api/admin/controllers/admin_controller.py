from fastapi import APIRouter
from app.api.admin.services import admin_service

router = APIRouter(prefix="/admins", tags=["admins"])



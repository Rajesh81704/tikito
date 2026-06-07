from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.auth.auth_controller import router as auth_router
from app.api.user.controllers.user_controller import router as user_router
from app.api.admin.controllers.admin_controller import router as admin_router
from app.api.vendor.controllers.vendor_controller import router as vendor_router
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(vendor_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/pay")
def payment_page():
    html_path = os.path.join(os.path.dirname(__file__), "payment", "pay.html")
    return FileResponse(html_path, media_type="text/html")

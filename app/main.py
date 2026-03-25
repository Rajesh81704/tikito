from fastapi import FastAPI
from app.api.auth.auth_controller import router as auth_router
from app.api.user.controllers.user_controller import router as user_router
from app.api.admin.controllers.admin_controller import router as admin_router
from app.api.vendor.controllers.vendor_controller import router as vendor_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(vendor_router)

@app.get("/health")
def health():
    return {"status": "ok"}

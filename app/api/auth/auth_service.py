from app.api.core.jwt_handler import create_access_token

def login(data: dict) -> dict:
    # TODO: validate credentials against DB based on role
    role = data.get("role")  # "user" | "admin" | "vendor"
    token = create_access_token({"sub": data.get("email"), "role": role})
    return {"access_token": token, "token_type": "bearer"}

def logout(data: dict) -> dict:
    # TODO: invalidate token / blacklist
    return {"message": "Logged out"}

def refresh_token(data: dict) -> dict:
    # TODO: validate refresh token and issue new access token
    return {}

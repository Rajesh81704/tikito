from sqlalchemy import text
from app.core.connectdb import get_connection
from app.api.core.jwt_handler import create_access_token

ROLE_TABLE_MAP = {
    "vendor": ("vendors", "vendor_id", "vendor_phone_no", "vendor_email_id"),
    "user":   ("users",   "user_id",   "phone_no",        "email"),
    "admin":  ("admins",  "admin_id",  "phone_no",        "email"),
}

def login(data: dict) -> dict:
    role = data.get("role")
    if role not in ROLE_TABLE_MAP:
        return {"error": "Invalid role"}

    table, id_col, phone_col, email_col = ROLE_TABLE_MAP[role]
    conn = get_connection()
    try:
        row = conn.execute(
            text(f"""
                SELECT {id_col}, password
                FROM {table}
                WHERE ({phone_col} = :identifier OR {email_col} = :identifier)
                AND is_active = true
            """),
            {"identifier": data.get("identifier")}
        ).fetchone()

        if not row:
            return {"error": f"{role.capitalize()} not found"}

        if row.password != data.get("password"):
            return {"error": "Invalid credentials"}

        token = create_access_token({"sub": str(row[0]), "role": role})
        return {"access_token": token, "token_type": "bearer"}
    finally:
        conn.close()

def logout() -> dict:
    return {"message": "Logged out"}

def refresh_token(data: dict) -> dict:
    return {}

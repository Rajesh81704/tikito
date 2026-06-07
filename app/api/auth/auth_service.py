from sqlalchemy import text
from app.core.connectdb import get_connection
from app.api.core.jwt_handler import create_access_token

ROLE_TABLE_MAP = {
    "vendor": ("vendors", "vendor_id", "vendor_phone_no", "vendor_email_id", "password"),
    "user":   ("users",   "user_id",   "phone_no",        "email",           "password"),
    "admin":  ("admins",  "admin_id",  "phone_no",        "email",           "password_hash"),
}

def login(data: dict) -> dict:
    role = data.get("role")
    if role not in ROLE_TABLE_MAP:
        return {"error": "Invalid role"}

    table, id_col, phone_col, email_col, pass_col = ROLE_TABLE_MAP[role]
    conn = get_connection()
    try:
        row = conn.execute(
            text(f"""
                SELECT {id_col}, {pass_col} AS password
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

def get_me(current_user: dict) -> dict:
    from sqlalchemy import text
    from app.core.connectdb import get_connection

    role = current_user.get("role")
    user_id = current_user.get("sub")

    ROLE_QUERY = {
        "user": (
            "SELECT user_id, full_name, phone_no, email, is_active, is_verified, created_at FROM users WHERE user_id = :id AND is_active = true",
            "user_id"
        ),
        "vendor": (
            "SELECT vendor_id, vendor_full_name, vendor_phone_no, vendor_email_id, vendor_address, is_active, created_at FROM vendors WHERE vendor_id = :id AND is_active = true",
            "vendor_id"
        ),
        "admin": (
            "SELECT admin_id, full_name, email, phone_no, role, is_active, created_at FROM admins WHERE admin_id = :id AND is_active = true",
            "admin_id"
        ),
    }

    if role not in ROLE_QUERY:
        raise Exception("Invalid role")

    query, _ = ROLE_QUERY[role]
    conn = get_connection()
    try:
        row = conn.execute(text(query), {"id": user_id}).mappings().fetchone()
        if not row:
            raise Exception("User not found")
        return {k: str(v) if hasattr(v, 'hex') else v for k, v in dict(row).items()}
    finally:
        conn.close()

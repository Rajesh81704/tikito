"""Forgot password flow using Resend for OTP emails."""
import os
import random
from dotenv import load_dotenv
from sqlalchemy import text
from app.core.connectdb import get_connection
from app.core.cache import redis_client

load_dotenv()

try:
    import resend
    resend.api_key = os.getenv("RESEND_API_KEY")
except ImportError:
    resend = None

FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")

OTP_EXPIRY_SECONDS = 300  # 5 minutes


def _generate_otp() -> str:
    return str(random.randint(100000, 999999))


def _find_user_by_email(email: str, role: str) -> dict | None:
    """Look up a user/vendor/admin by email."""
    ROLE_MAP = {
        "user": ("users", "user_id", "email"),
        "vendor": ("vendors", "vendor_id", "vendor_email_id"),
        "admin": ("admins", "admin_id", "email"),
    }

    if role not in ROLE_MAP:
        return None

    table, id_col, email_col = ROLE_MAP[role]
    conn = get_connection()
    try:
        row = conn.execute(
            text(f"SELECT {id_col} FROM {table} WHERE {email_col} = :email AND is_active = true"),
            {"email": email}
        ).fetchone()
        return {"id": str(row[0]), "table": table, "id_col": id_col} if row else None
    finally:
        conn.close()


def forgot_password(email: str, role: str) -> dict:
    """Send a password reset OTP to the user's email."""
    user = _find_user_by_email(email, role)
    if not user:
        return {"message": "If this email is registered, you will receive a reset code."}

    otp = _generate_otp()

    # Store OTP in Redis with expiry
    redis_client.setex(f"otp:{email}", OTP_EXPIRY_SECONDS, f"{otp}:{role}")

    # Send OTP via Resend
    resend.Emails.send({
        "from": FROM_EMAIL,
        "to": [email],
        "subject": "Tikito - Password Reset Code",
        "html": f"""
            <h2>Password Reset</h2>
            <p>Your password reset code is:</p>
            <h1 style="letter-spacing: 4px; font-size: 36px; color: #4F46E5;">{otp}</h1>
            <p>This code expires in 5 minutes.</p>
            <p>If you didn't request this, please ignore this email.</p>
        """,
    })

    return {"message": "If this email is registered, you will receive a reset code."}


def verify_otp(email: str, otp: str) -> dict:
    """Verify the OTP sent to the user's email."""
    stored = redis_client.get(f"otp:{email}")

    if not stored:
        raise Exception("No reset request found or code expired. Please request a new one.")

    stored_otp, role = stored.split(":")

    if stored_otp != otp:
        raise Exception("Invalid code.")

    # Mark as verified in Redis (new key with short TTL for reset step)
    redis_client.setex(f"otp_verified:{email}", 600, role)
    redis_client.delete(f"otp:{email}")

    return {"message": "Code verified. You can now reset your password.", "email": email}


def reset_password(email: str, new_password: str) -> dict:
    """Reset the password after OTP verification."""
    role = redis_client.get(f"otp_verified:{email}")

    if not role:
        raise Exception("Please verify your OTP first.")

    user = _find_user_by_email(email, role)
    if not user:
        raise Exception("User not found.")

    conn = get_connection()
    try:
        conn.execute(
            text(f"UPDATE {user['table']} SET password = :password WHERE {user['id_col']} = :id"),
            {"password": new_password, "id": user["id"]}
        )
        conn.commit()

        # Clean up Redis
        redis_client.delete(f"otp_verified:{email}")

        return {"message": "Password reset successfully."}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

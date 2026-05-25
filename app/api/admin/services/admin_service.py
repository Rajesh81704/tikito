"""Admin service — manages users, vendors, turfs, grounds, and bookings."""
from sqlalchemy import text
from app.core.connectdb import get_connection


def _serialize(row: dict) -> dict:
    return {k: str(v) if hasattr(v, 'hex') else v for k, v in row.items()}


# ─── Dashboard / Stats ────────────────────────────────────────────────────────

def get_dashboard() -> dict:
    conn = get_connection()
    try:
        row = conn.execute(text("""
            SELECT
                (SELECT COUNT(*) FROM users WHERE is_active = true) AS total_users,
                (SELECT COUNT(*) FROM vendors WHERE is_active = true) AS total_vendors,
                (SELECT COUNT(*) FROM turf_fields WHERE is_active = true) AS total_turfs,
                (SELECT COUNT(*) FROM turf_grounds WHERE is_active = true) AS total_grounds,
                (SELECT COUNT(*) FROM bookings) AS total_bookings,
                (SELECT COUNT(*) FROM bookings WHERE booking_status = 'CONFIRMED') AS confirmed_bookings,
                (SELECT COUNT(*) FROM bookings WHERE booking_status = 'CANCELLED') AS cancelled_bookings,
                (SELECT COALESCE(SUM(s.price), 0) FROM bookings b JOIN turf_slots s ON s.slot_id = b.slot_id WHERE b.booking_status = 'CONFIRMED') AS total_revenue
        """)).mappings().fetchone()
        return dict(row)
    finally:
        conn.close()


# ─── User Management ──────────────────────────────────────────────────────────

def get_all_users() -> list:
    conn = get_connection()
    try:
        rows = conn.execute(text(
            "SELECT user_id, full_name, phone_no, email, is_active, is_verified, created_at FROM users ORDER BY created_at DESC"
        )).mappings().all()
        return [_serialize(dict(r)) for r in rows]
    finally:
        conn.close()


def get_user_by_id(user_id: str) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            text("SELECT user_id, full_name, phone_no, email, is_active, is_verified, created_at FROM users WHERE user_id = :id"),
            {"id": user_id}
        ).mappings().fetchone()
        if not row:
            raise Exception("User not found")
        return _serialize(dict(row))
    finally:
        conn.close()


def toggle_user_status(user_id: str, is_active: bool) -> dict:
    conn = get_connection()
    try:
        result = conn.execute(
            text("UPDATE users SET is_active = :is_active, updated_at = CURRENT_TIMESTAMP WHERE user_id = :id RETURNING user_id"),
            {"is_active": is_active, "id": user_id}
        ).fetchone()
        if not result:
            raise Exception("User not found")
        conn.commit()
        action = "activated" if is_active else "deactivated"
        return {"message": f"User {action} successfully", "user_id": user_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def delete_user(user_id: str) -> dict:
    conn = get_connection()
    try:
        result = conn.execute(
            text("DELETE FROM users WHERE user_id = :id RETURNING user_id"),
            {"id": user_id}
        ).fetchone()
        if not result:
            raise Exception("User not found")
        conn.commit()
        return {"message": "User deleted permanently", "user_id": user_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# ─── Vendor Management ────────────────────────────────────────────────────────

def get_all_vendors() -> list:
    conn = get_connection()
    try:
        rows = conn.execute(text(
            "SELECT vendor_id, vendor_full_name, vendor_phone_no, vendor_email_id, vendor_address, is_active, is_verified, created_at FROM vendors ORDER BY created_at DESC"
        )).mappings().all()
        return [_serialize(dict(r)) for r in rows]
    finally:
        conn.close()


def get_vendor_by_id(vendor_id: str) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            text("SELECT vendor_id, vendor_full_name, vendor_phone_no, vendor_email_id, vendor_address, is_active, is_verified, created_at FROM vendors WHERE vendor_id = :id"),
            {"id": vendor_id}
        ).mappings().fetchone()
        if not row:
            raise Exception("Vendor not found")
        return _serialize(dict(row))
    finally:
        conn.close()


def verify_vendor(vendor_id: str) -> dict:
    conn = get_connection()
    try:
        result = conn.execute(
            text("UPDATE vendors SET is_verified = true, updated_at = CURRENT_TIMESTAMP WHERE vendor_id = :id RETURNING vendor_id"),
            {"id": vendor_id}
        ).fetchone()
        if not result:
            raise Exception("Vendor not found")
        conn.commit()
        return {"message": "Vendor verified successfully", "vendor_id": vendor_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def toggle_vendor_status(vendor_id: str, is_active: bool) -> dict:
    conn = get_connection()
    try:
        result = conn.execute(
            text("UPDATE vendors SET is_active = :is_active, updated_at = CURRENT_TIMESTAMP WHERE vendor_id = :id RETURNING vendor_id"),
            {"is_active": is_active, "id": vendor_id}
        ).fetchone()
        if not result:
            raise Exception("Vendor not found")
        conn.commit()
        action = "activated" if is_active else "deactivated"
        return {"message": f"Vendor {action} successfully", "vendor_id": vendor_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def delete_vendor(vendor_id: str) -> dict:
    conn = get_connection()
    try:
        result = conn.execute(
            text("DELETE FROM vendors WHERE vendor_id = :id RETURNING vendor_id"),
            {"id": vendor_id}
        ).fetchone()
        if not result:
            raise Exception("Vendor not found")
        conn.commit()
        return {"message": "Vendor deleted permanently (cascades to turfs/grounds/slots)", "vendor_id": vendor_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# ─── Turf Management ─────────────────────────────────────────────────────────

def get_all_turfs() -> list:
    conn = get_connection()
    try:
        rows = conn.execute(text("""
            SELECT tf.turf_field_id, tf.turf_name, tf.turf_location, tf.turf_address,
                   tf.no_of_grounds, tf.is_active, tf.created_at,
                   v.vendor_full_name, v.vendor_id
            FROM turf_fields tf
            JOIN vendors v ON v.vendor_id = tf.vendor_id
            ORDER BY tf.created_at DESC
        """)).mappings().all()
        return [_serialize(dict(r)) for r in rows]
    finally:
        conn.close()


def toggle_turf_status(turf_field_id: str, is_active: bool) -> dict:
    conn = get_connection()
    try:
        result = conn.execute(
            text("UPDATE turf_fields SET is_active = :is_active, updated_at = CURRENT_TIMESTAMP WHERE turf_field_id = :id RETURNING turf_field_id"),
            {"is_active": is_active, "id": turf_field_id}
        ).fetchone()
        if not result:
            raise Exception("Turf not found")
        conn.commit()
        action = "activated" if is_active else "deactivated"
        return {"message": f"Turf {action} successfully", "turf_field_id": turf_field_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def delete_turf(turf_field_id: str) -> dict:
    conn = get_connection()
    try:
        result = conn.execute(
            text("DELETE FROM turf_fields WHERE turf_field_id = :id RETURNING turf_field_id"),
            {"id": turf_field_id}
        ).fetchone()
        if not result:
            raise Exception("Turf not found")
        conn.commit()
        return {"message": "Turf deleted permanently (cascades to grounds/slots/bookings)", "turf_field_id": turf_field_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# ─── Booking Management ──────────────────────────────────────────────────────

def get_all_bookings() -> list:
    conn = get_connection()
    try:
        rows = conn.execute(text("""
            SELECT b.booking_id, b.booking_date, b.booking_status, b.payment_status,
                   b.booked_at, b.razorpay_order_id, b.razorpay_payment_id,
                   s.start_time, s.end_time, s.price, s.day_of_week,
                   g.ground_name, g.ground_type,
                   tf.turf_name, tf.turf_address,
                   u.full_name AS user_name, u.phone_no AS user_phone
            FROM bookings b
            JOIN turf_slots s ON s.slot_id = b.slot_id
            JOIN turf_grounds g ON g.turf_ground_id = s.turf_ground_id
            JOIN turf_fields tf ON tf.turf_field_id = g.turf_field_id
            LEFT JOIN users u ON u.user_id = b.user_id
            ORDER BY b.booked_at DESC
        """)).mappings().all()
        return [_serialize(dict(r)) for r in rows]
    finally:
        conn.close()


def cancel_booking(booking_id: str) -> dict:
    conn = get_connection()
    try:
        result = conn.execute(
            text("UPDATE bookings SET booking_status = 'CANCELLED', is_available = false WHERE booking_id = :id RETURNING booking_id"),
            {"id": booking_id}
        ).fetchone()
        if not result:
            raise Exception("Booking not found")
        conn.commit()
        return {"message": "Booking cancelled by admin", "booking_id": booking_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def delete_booking(booking_id: str) -> dict:
    conn = get_connection()
    try:
        result = conn.execute(
            text("DELETE FROM bookings WHERE booking_id = :id RETURNING booking_id"),
            {"id": booking_id}
        ).fetchone()
        if not result:
            raise Exception("Booking not found")
        conn.commit()
        return {"message": "Booking deleted permanently", "booking_id": booking_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

from sqlalchemy import text
from app.core.connectdb import get_connection

def signup(data: dict) -> dict:
    conn = get_connection()
    try:

        check_availability=conn.execute(
            text("SELECT vendor_phone_no, vendor_email_id from vendors where "),
        )
        result = conn.execute(
            text("""
                INSERT INTO vendors (vendor_full_name, vendor_phone_no, vendor_email_id, vendor_address)
                VALUES (:vendor_full_name, :vendor_phone_no, :vendor_email_id, :vendor_address, :password)
                RETURNING vendor_id
            """),
            {
                "vendor_full_name": data.get("vendor_full_name"),
                "vendor_phone_no": data.get("vendor_phone_no"),
                "vendor_email_id": data.get("vendor_email_id"),
                "vendor_address": data.get("vendor_address"),
                "password": data.get("password")
            }
        )
        vendor_id = result.fetchone()[0]
        conn.commit()
        return {"vendor_id": str(vendor_id), "message": "Vendor registered successfully"}
    finally:
        conn.close()

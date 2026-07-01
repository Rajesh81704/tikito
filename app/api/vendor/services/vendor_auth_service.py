from sqlalchemy import text
from app.core.connectdb import get_connection

def signup(data: dict) -> dict:
    conn = get_connection()
    try:
        # Build dynamic query to check for existing vendor
        conditions = []
        params = {}
        
        if data.get("vendor_phone_no"):
            conditions.append("vendor_phone_no = :vendor_phone_no")
            params["vendor_phone_no"] = data.get("vendor_phone_no")
        
        if data.get("vendor_email_id"):
            conditions.append("vendor_email_id = :vendor_email_id")
            params["vendor_email_id"] = data.get("vendor_email_id")
        
        # Only check if at least one identifier is provided
        if conditions:
            query = f"SELECT vendor_id FROM vendors WHERE {' OR '.join(conditions)}"
            existing = conn.execute(text(query), params).fetchone()
            if existing:
                return {"error": "Vendor with this phone or email already exists"}
        
        # Ensure at least email or phone is provided
        if not data.get("vendor_phone_no") and not data.get("vendor_email_id"):
            return {"error": "Either phone number or email must be provided"}

        result = conn.execute(
            text("""
                INSERT INTO vendors (vendor_full_name, vendor_phone_no, vendor_email_id, vendor_address, password)
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

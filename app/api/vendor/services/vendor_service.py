from sqlalchemy import text
from app.core.connectdb import get_connection
def get_all():
    pass

def get_by_id(vendor_id: int):
    pass

def create(data: dict):
    pass

def update(vendor_id: int, data: dict):
    pass

def delete(vendor_id: int):
    pass


def add_turf(data: dict, current_user: dict) -> dict:
    conn = get_connection()
    try:
        vendor_id = current_user.get("sub")
        print(vendor_id)
        query = text("""
        INSERT INTO turf_fields (turf_name, turf_location, turf_address, no_of_grounds, vendor_id, turf_facilities, turf_rules)
        VALUES (:turf_name, :turf_location, :turf_address, :no_of_grounds, :vendor_id, :turf_facilities, :turf_rules)
        RETURNING turf_field_id
        """)
        result = conn.execute(query, {
            "turf_name": data.get("turf_name"),
            "turf_location": data.get("turf_location"),
            "turf_address": data.get("turf_address"),
            "no_of_grounds": data.get("no_of_grounds"),
            "vendor_id": vendor_id,
            "turf_facilities": data.get("turf_facilities"),
            "turf_rules": data.get("turf_rules")
        })
        conn.commit()
        turf_field_id = result.fetchone()[0]
        return {"turf_field_id": str(turf_field_id)}
    
    except Exception as e:
        conn.rollback()
        raise e

def add_ground(data: dict, current_user: dict) -> dict:
    conn = get_connection()
    try:
        check_turf = conn.execute(
            text("SELECT 1 FROM turf_fields WHERE turf_field_id = :turf_field_id"),
            {"turf_field_id": data.get("turf_field_id")}
        )

        if not check_turf.fetchone():
            raise Exception("Invalid turf")
        
        result = conn.execute(
            text("""
                INSERT INTO turf_grounds (ground_name, ground_loc, ground_type, turf_field_id)
                VALUES (:ground_name, :ground_loc, :ground_type, :turf_field_id)
                RETURNING turf_ground_id
            """),
            {
                "ground_name": data.get("ground_name"),
                "ground_loc": data.get("ground_loc"),
                "ground_type": data.get("ground_type"),
                "turf_field_id": data.get("turf_field_id")
            }
        ) 
        turf_ground_id = result.fetchone()[0]
        
        slots = data.get("slots", [])
        for slot in slots:
            conn.execute(
                text("""
                    INSERT INTO turf_slots (turf_ground_id, day_of_week, start_time, end_time, price, is_peak)
                    VALUES (:turf_ground_id, :day_of_week, :start_time, :end_time, :price, :is_peak)
                """),
                {
                    "turf_ground_id": str(turf_ground_id),
                    "day_of_week": slot.get("day_of_week"),
                    "start_time": slot.get("start_time"),
                    "end_time": slot.get("end_time"),
                    "price": slot.get("price"),
                    "is_peak": slot.get("is_peak", False)
                }
            )

        conn.commit()
        return {"turf_ground_id": str(turf_ground_id), "slots_added": len(slots)}

    except Exception as e:
        conn.rollback()
        raise e

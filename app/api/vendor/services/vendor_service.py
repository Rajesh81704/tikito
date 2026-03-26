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

def edit_turf(turf_field_id: str, data: dict, current_user: dict) -> dict:
    conn = get_connection()
    try:
        allowed = {"turf_name", "turf_location", "turf_address", "no_of_grounds", "turf_facilities", "turf_rules"}
        fields = {k: v for k, v in data.items() if k in allowed}
        if not fields:
            raise Exception("No valid fields to update")

        set_clause = ", ".join(f"{k} = :{k}" for k in fields)
        fields["turf_field_id"] = turf_field_id
        fields["vendor_id"] = current_user.get("sub")

        result = conn.execute(
            text(f"""
                UPDATE turf_fields
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE turf_field_id = :turf_field_id AND vendor_id = :vendor_id
                RETURNING turf_field_id
            """),
            fields
        )
        row = result.fetchone()
        if not row:
            raise Exception("Turf not found or unauthorized")
        conn.commit()
        return {"turf_field_id": str(row[0]), "message": "Turf updated successfully"}
    except Exception as e:
        conn.rollback()
        raise e


def edit_ground(turf_ground_id: str, data: dict, current_user: dict) -> dict:
    conn = get_connection()
    try:
        allowed = {"ground_name", "ground_loc", "ground_type"}
        fields = {k: v for k, v in data.items() if k in allowed}

        if fields:
            set_clause = ", ".join(f"{k} = :{k}" for k in fields)
            fields["turf_ground_id"] = turf_ground_id
            result = conn.execute(
                text(f"""
                    UPDATE turf_grounds
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE turf_ground_id = :turf_ground_id
                    RETURNING turf_ground_id
                """),
                fields
            )
            if not result.fetchone():
                raise Exception("Ground not found")

        slots = data.get("slots")
        if slots is not None:
            conn.execute(
                text("DELETE FROM turf_slots WHERE turf_ground_id = :turf_ground_id"),
                {"turf_ground_id": turf_ground_id}
            )
            for slot in slots:
                conn.execute(
                    text("""
                        INSERT INTO turf_slots (turf_ground_id, day_of_week, start_time, end_time, price, is_peak)
                        VALUES (:turf_ground_id, :day_of_week, :start_time, :end_time, :price, :is_peak)
                    """),
                    {
                        "turf_ground_id": turf_ground_id,
                        "day_of_week": slot.get("day_of_week"),
                        "start_time": slot.get("start_time"),
                        "end_time": slot.get("end_time"),
                        "price": slot.get("price"),
                        "is_peak": slot.get("is_peak", False)
                    }
                )

        conn.commit()
        return {"turf_ground_id": turf_ground_id, "message": "Ground updated successfully"}
    except Exception as e:
        conn.rollback()
        raise e

def _serialize(row: dict) -> dict:
    return {k: str(v) if hasattr(v, 'hex') else v for k, v in row.items()}

def get_turfs_by_vendor(current_user: dict) -> list:
    conn = get_connection()
    try:
        result = conn.execute(
            text("SELECT * FROM turf_fields WHERE vendor_id = :vendor_id AND is_active = true"),
            {"vendor_id": current_user.get("sub")}
        )
        rows = result.mappings().all()
        return [_serialize(dict(row)) for row in rows]
    finally:
        conn.close()

def get_grounds_by_turf(turf_field_id: str) -> list:
    conn = get_connection()
    try:
        result = conn.execute(
            text("""
                SELECT g.*, 
                       json_agg(
                           json_build_object(
                               'slot_id', s.slot_id,
                               'day_of_week', s.day_of_week,
                               'start_time', s.start_time,
                               'end_time', s.end_time,
                               'price', s.price,
                               'is_peak', s.is_peak
                           ) ORDER BY s.day_of_week, s.start_time
                       ) AS slots
                FROM turf_grounds g
                LEFT JOIN turf_slots s ON s.turf_ground_id = g.turf_ground_id
                WHERE g.turf_field_id = :turf_field_id
                GROUP BY g.turf_ground_id
            """),
            {"turf_field_id": turf_field_id}
        )
        rows = result.mappings().all()
        return [_serialize(dict(row)) for row in rows]
    finally:
        conn.close()

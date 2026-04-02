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
        INSERT INTO turf_fields (turf_name, turf_location, turf_address, no_of_grounds, vendor_id, turf_facilities, turf_rules, latitude, longitude)
        VALUES (:turf_name, :turf_location, :turf_address, :no_of_grounds, :vendor_id, :turf_facilities, :turf_rules, :latitude, :longitude)
        RETURNING turf_field_id
        """)
        result = conn.execute(query, {
            "turf_name": data.get("turf_name"),
            "turf_location": data.get("turf_location"),
            "turf_address": data.get("turf_address"),
            "no_of_grounds": data.get("no_of_grounds"),
            "vendor_id": vendor_id,
            "turf_facilities": data.get("turf_facilities"),
            "turf_rules": data.get("turf_rules"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude")
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
                INSERT INTO turf_grounds (ground_name, ground_loc, ground_type, turf_field_id, booking_weeks)
                VALUES (:ground_name, :ground_loc, :ground_type, :turf_field_id, :booking_weeks)
                RETURNING turf_ground_id
            """),
            {
                "ground_name": data.get("ground_name"),
                "ground_loc": data.get("ground_loc"),
                "ground_type": data.get("ground_type"),
                "turf_field_id": data.get("turf_field_id"),
                "booking_weeks": data.get("booking_weeks", 1)
            }
        ) 
        turf_ground_id = result.fetchone()[0]

        schedule = data.get("schedule", [])
        total_slots = 0
        for day_entry in schedule:
            day_of_week = day_entry.get("day_of_week")
            for slot in day_entry.get("slots", []):
                conn.execute(
                    text("""
                        INSERT INTO turf_slots (turf_ground_id, day_of_week, start_time, end_time, price, is_peak)
                        VALUES (:turf_ground_id, :day_of_week, :start_time, :end_time, :price, :is_peak)
                    """),
                    {
                        "turf_ground_id": str(turf_ground_id),
                        "day_of_week": day_of_week,
                        "start_time": slot.get("start_time"),
                        "end_time": slot.get("end_time"),
                        "price": slot.get("price"),
                        "is_peak": slot.get("is_peak", False)
                    }
                )
                total_slots += 1

        conn.commit()
        return {"turf_ground_id": str(turf_ground_id), "slots_added": total_slots}

    except Exception as e:
        conn.rollback()
        raise e

def edit_turf(turf_field_id: str, data: dict, current_user: dict) -> dict:
    conn = get_connection()
    try:
        allowed = {"turf_name", "turf_location", "turf_address", "no_of_grounds", "turf_facilities", "turf_rules", "latitude", "longitude"}
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
        allowed = {"ground_name", "ground_loc", "ground_type", "booking_weeks"}
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

        slots = data.get("schedule")
        if slots is not None:
            conn.execute(
                text("DELETE FROM turf_slots WHERE turf_ground_id = :turf_ground_id"),
                {"turf_ground_id": turf_ground_id}
            )
            for day_entry in slots:
                day_of_week = day_entry.get("day_of_week")
                for slot in day_entry.get("slots", []):
                    conn.execute(
                        text("""
                            INSERT INTO turf_slots (turf_ground_id, day_of_week, start_time, end_time, price, is_peak)
                            VALUES (:turf_ground_id, :day_of_week, :start_time, :end_time, :price, :is_peak)
                        """),
                        {
                            "turf_ground_id": turf_ground_id,
                            "day_of_week": day_of_week,
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

def get_turf_location(turf_field_id: str) -> dict:
    import httpx
    conn = get_connection()
    try:
        row = conn.execute(
            text("SELECT turf_address, turf_name FROM turf_fields WHERE turf_field_id = :turf_field_id"),
            {"turf_field_id": turf_field_id}
        ).fetchone()

        if not row:
            raise Exception("Turf not found")

        response = httpx.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": row.turf_address, "format": "json", "limit": 1},
            headers={"User-Agent": "tikito-app"}
        )
        data = response.json()
        if not data:
            return {"error": "Could not geocode address", "address": row.turf_address}

        return {
            "turf_name": row.turf_name,
            "address": row.turf_address,
            "latitude": data[0]["lat"],
            "longitude": data[0]["lon"]
        }
    finally:
        conn.close()

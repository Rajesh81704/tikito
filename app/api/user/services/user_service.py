from sqlalchemy import text
from app.core.connectdb import get_connection

def create(data: dict) -> dict:
    conn = get_connection()
    try:
        existing = conn.execute(
            text("SELECT user_id FROM users WHERE phone_no = :phone_no OR email = :email"),
            {"phone_no": data.get("phone_no"), "email": data.get("email")}
        ).fetchone()
        if existing:
            return {"error": "User with this phone or email already exists"}

        result = conn.execute(
            text("""
                INSERT INTO users (full_name, phone_no, email, password)
                VALUES (:full_name, :phone_no, :email, :password)
                RETURNING user_id
            """),
            {
                "full_name": data.get("full_name"),
                "phone_no": data.get("phone_no"),
                "email": data.get("email"),
                "password": data.get("password")
            }
        )
        user_id = result.fetchone()[0]
        conn.commit()
        return {"user_id": str(user_id), "message": "User registered successfully"}
    finally:
        conn.close()

def get_nearby_turfs(lat: float, lng: float, radius_km: float) -> list:
    import httpx
    from math import radians, sin, cos, sqrt, atan2

    def haversine(lat1, lon1, lat2, lon2) -> float:
        R = 6371  # Earth radius in km
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        return R * 2 * atan2(sqrt(a), sqrt(1 - a))

    conn = get_connection()
    try:
        rows = conn.execute(
            text("SELECT turf_field_id, turf_name, turf_address, turf_location FROM turf_fields WHERE is_active = true")
        ).mappings().all()

        nearby = []
        for row in rows:
            if not row["turf_address"]:
                continue
            res = httpx.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": row["turf_address"], "format": "json", "limit": 1},
                headers={"User-Agent": "tikito-app"}
            ).json()
            if not res:
                continue
            turf_lat = float(res[0]["lat"])
            turf_lng = float(res[0]["lon"])
            distance = haversine(lat, lng, turf_lat, turf_lng)
            if distance <= radius_km:
                nearby.append({
                    "turf_field_id": str(row["turf_field_id"]),
                    "turf_name": row["turf_name"],
                    "turf_address": row["turf_address"],
                    "turf_location": row["turf_location"],
                    "latitude": turf_lat,
                    "longitude": turf_lng,
                    "distance_km": round(distance, 2)
                })

        return sorted(nearby, key=lambda x: x["distance_km"])
    finally:
        conn.close()

def get_turfs_by_city(city: str) -> list:
    conn = get_connection()
    try:
        rows = conn.execute(
            text("""
                SELECT turf_field_id, turf_name, turf_location, turf_address,
                       no_of_grounds, turf_facilities, turf_rules
                FROM turf_fields
                WHERE is_active = true
                AND turf_location ILIKE :city
            """),
            {"city": f"%{city}%"}
        ).mappings().all()
        return [
            {k: str(v) if hasattr(v, 'hex') else v for k, v in dict(row).items()}
            for row in rows
        ]
    finally:
        conn.close()

def get_available_slots(turf_ground_id: str) -> list:
    from datetime import date, timedelta

    DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

    conn = get_connection()
    try:
        # Get ground booking_weeks config
        ground = conn.execute(
            text("SELECT booking_weeks FROM turf_grounds WHERE turf_ground_id = :id"),
            {"id": turf_ground_id}
        ).fetchone()

        if not ground:
            raise Exception("Ground not found")

        booking_weeks = ground.booking_weeks
        today = date.today()
        end_date = today + timedelta(days=(booking_weeks * 7) - 1)

        # Get all slot templates for this ground
        slots = conn.execute(
            text("""
                SELECT slot_id, day_of_week, start_time, end_time, price, is_peak
                FROM turf_slots WHERE turf_ground_id = :id
            """),
            {"id": turf_ground_id}
        ).mappings().all()

        # Get already booked slot+date combos in the window
        booked = conn.execute(
            text("""
                SELECT slot_id, booking_date FROM bookings
                WHERE slot_id IN (
                    SELECT slot_id FROM turf_slots WHERE turf_ground_id = :id
                )
                AND booking_date BETWEEN :start AND :end
                AND booking_status != 'CANCELLED'
            """),
            {"id": turf_ground_id, "start": today, "end": end_date}
        ).fetchall()

        booked_set = {(str(b[0]), str(b[1])) for b in booked}

        # Build available slots per date
        result = []
        current = today
        while current <= end_date:
            day_name = DAYS[current.weekday()]
            for slot in slots:
                if slot["day_of_week"] == day_name:
                    slot_id = str(slot["slot_id"])
                    if (slot_id, str(current)) not in booked_set:
                        result.append({
                            "slot_id": slot_id,
                            "date": str(current),
                            "day_of_week": day_name,
                            "start_time": str(slot["start_time"]),
                            "end_time": str(slot["end_time"]),
                            "price": float(slot["price"]),
                            "is_peak": slot["is_peak"]
                        })
            current += timedelta(days=1)

        return result
    finally:
        conn.close()


def book_slot(data: dict, current_user: dict) -> dict:
    from datetime import date

    conn = get_connection()
    try:
        slot_id = data.get("slot_id")
        booking_date = data.get("booking_date")
        user_id = current_user.get("sub")

        # Validate slot exists
        slot = conn.execute(
            text("SELECT slot_id, turf_ground_id FROM turf_slots WHERE slot_id = :slot_id"),
            {"slot_id": slot_id}
        ).fetchone()
        if not slot:
            raise Exception("Slot not found")

        # Validate booking_date is within allowed window
        ground = conn.execute(
            text("SELECT booking_weeks FROM turf_grounds WHERE turf_ground_id = :id"),
            {"id": str(slot.turf_ground_id)}
        ).fetchone()

        from datetime import timedelta
        today = date.today()
        max_date = today + timedelta(weeks=ground.booking_weeks)
        bdate = date.fromisoformat(booking_date)

        if bdate < today or bdate > max_date:
            raise Exception(f"Booking date must be between {today} and {max_date}")

        # Check day_of_week matches
        DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
        slot_day = conn.execute(
            text("SELECT day_of_week FROM turf_slots WHERE slot_id = :slot_id"),
            {"slot_id": slot_id}
        ).fetchone()

        if slot_day.day_of_week != DAYS[bdate.weekday()]:
            raise Exception(f"Slot is not available on {bdate.strftime('%A')}")

        # Insert booking
        result = conn.execute(
            text("""
                INSERT INTO bookings (slot_id, user_id, booking_date, booking_status)
                VALUES (:slot_id, :user_id, :booking_date, 'CONFIRMED')
                RETURNING booking_id
            """),
            {"slot_id": slot_id, "user_id": user_id, "booking_date": booking_date}
        )
        booking_id = result.fetchone()[0]
        conn.commit()
        return {"booking_id": str(booking_id), "message": "Slot booked successfully"}

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

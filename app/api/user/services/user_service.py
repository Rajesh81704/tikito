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
            text("SELECT turf_field_id, turf_name, turf_address, turf_location, turf_images FROM turf_fields WHERE is_active = true")
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
                import json
                images = []
                if row["turf_images"]:
                    try:
                        images = json.loads(row["turf_images"])
                    except (json.JSONDecodeError, TypeError):
                        images = [row["turf_images"]] if row["turf_images"] else []

                nearby.append({
                    "turf_field_id": str(row["turf_field_id"]),
                    "turf_name": row["turf_name"],
                    "turf_address": row["turf_address"],
                    "turf_location": row["turf_location"],
                    "turf_images": images,
                    "latitude": turf_lat,
                    "longitude": turf_lng,
                    "distance_km": round(distance, 2)
                })

        return sorted(nearby, key=lambda x: x["distance_km"])
    finally:
        conn.close()

def get_turfs_by_city(city: str) -> list:
    """Get turfs by city."""
    import json
    from decimal import Decimal

    conn = get_connection()
    try:
        rows = conn.execute(
            text("""
                SELECT turf_field_id, turf_name, turf_location, turf_address,
                       no_of_grounds, turf_facilities, turf_rules, turf_images,
                       latitude, longitude
                FROM turf_fields
                WHERE is_active = true
                AND turf_location ILIKE :city
            """),
            {"city": f"%{city}%"}
        ).mappings().all()
        result = []
        for row in rows:
            item = {}
            for k, v in dict(row).items():
                if hasattr(v, 'hex'):
                    item[k] = str(v)
                elif isinstance(v, Decimal):
                    item[k] = str(v)
                else:
                    item[k] = v
            # Parse turf_images from JSON string to array
            if item.get("turf_images"):
                try:
                    item["turf_images"] = json.loads(item["turf_images"])
                except (json.JSONDecodeError, TypeError):
                    item["turf_images"] = [item["turf_images"]] if item["turf_images"] else []
            else:
                item["turf_images"] = []
            result.append(item)
        return result
    finally:
        conn.close()

def get_available_slots(turf_ground_id: str) -> list:
    """Get available slots."""
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

        booking_weeks = ground.booking_weeks or 1
        today = date.today()
        end_date = today + timedelta(days=(booking_weeks * 7) - 1)

        print(f"booking_weeks: {booking_weeks}, today: {today}, end_date: {end_date}")

        slots = conn.execute(
            text("""
                SELECT slot_id, day_of_week, start_time, end_time, price, is_peak
                FROM turf_slots WHERE turf_ground_id = :id
            """),
            {"id": turf_ground_id}
        ).mappings().all()

        print(f"slots found: {len(slots)}, slots: {[dict(s) for s in slots]}")

        # Get already booked slot ids (active bookings - both PENDING and CONFIRMED)
        booked = conn.execute(
            text("""
                SELECT slot_id FROM bookings
                WHERE slot_id IN (
                    SELECT slot_id FROM turf_slots WHERE turf_ground_id = :id
                )
                AND booking_status IN ('PENDING', 'CONFIRMED')
            """),
            {"id": turf_ground_id}
        ).fetchall()

        booked_set = {str(b[0]) for b in booked}

        # Build available slots per date
        result = []
        current = today
        while current <= end_date:
            day_name = DAYS[current.weekday()]
            for slot in slots:
                if slot["day_of_week"] == day_name:
                    slot_id = str(slot["slot_id"])
                    if slot_id not in booked_set:
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
        user_id = current_user.get("sub")

        slot = conn.execute(
            text("SELECT slot_id, turf_ground_id FROM turf_slots WHERE slot_id = :slot_id"),
            {"slot_id": slot_id}
        ).fetchone()
        if not slot:
            raise Exception("Slot not found")

        result = conn.execute(
            text("""
                INSERT INTO bookings (slot_id, user_id, booking_date, booking_status, is_available, payment_status)
                VALUES (:slot_id, :user_id, :booking_date, 'PENDING', true, 'PENDING')
                RETURNING booking_id
            """),
            {"slot_id": slot_id, "user_id": user_id, "booking_date": date.today()}
        )
        booking_id = result.fetchone()[0]
        conn.commit()

        return {"booking_id": str(booking_id), "message": "Slot booked successfully"}

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_my_bookings(current_user: dict) -> list:
    conn = get_connection()
    try:
        rows = conn.execute(
            text("""
                SELECT b.booking_id, b.booking_date, b.booking_status, b.payment_status,
                       b.is_available, b.booked_at,
                       s.start_time, s.end_time, s.price, s.day_of_week,
                       g.ground_name, g.ground_type,
                       tf.turf_name, tf.turf_address
                FROM bookings b
                JOIN turf_slots s ON s.slot_id = b.slot_id
                JOIN turf_grounds g ON g.turf_ground_id = s.turf_ground_id
                JOIN turf_fields tf ON tf.turf_field_id = g.turf_field_id
                WHERE b.user_id = :user_id
                AND b.booking_status != 'CANCELLED'
                ORDER BY b.booked_at DESC
            """),
            {"user_id": current_user.get("sub")}
        ).mappings().all()
        return [
            {k: str(v) if hasattr(v, 'hex') else v for k, v in dict(row).items()}
            for row in rows
        ]
    finally:
        conn.close()

def soft_delete_user(current_user: dict) -> dict:
    conn = get_connection()
    try:
        conn.execute(
            text("UPDATE users SET is_active = false WHERE user_id = :user_id"),
            {"user_id": current_user.get("sub")}
        )
        conn.commit()
        return {"message": "Account deactivated successfully"}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

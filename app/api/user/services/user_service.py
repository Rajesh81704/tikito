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

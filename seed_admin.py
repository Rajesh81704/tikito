"""One-time script to seed the admin user into the database."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DB_URL = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    f"?sslmode={os.getenv('DB_SSLMODE')}"
)

engine = create_engine(DB_URL)

def seed_admin():
    conn = engine.connect()
    try:
        # Check if admin already exists
        existing = conn.execute(
            text("SELECT admin_id FROM admins WHERE email = :email"),
            {"email": "tikitoapp@gmail.com"}
        ).fetchone()

        if existing:
            print("Admin already exists, skipping.")
            return

        conn.execute(
            text("""
                INSERT INTO admins (full_name, email, password_hash, role, is_active)
                VALUES (:full_name, :email, :password_hash, :role, :is_active)
            """),
            {
                "full_name": "Tikito Admin",
                "email": "tikitoapp@gmail.com",
                "password_hash": "tikito123",
                "role": "SUPER_ADMIN",
                "is_active": True,
            }
        )
        conn.commit()
        print("Admin seeded successfully!")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_admin()

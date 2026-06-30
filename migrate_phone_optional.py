"""Migration script to make phone_no optional in users table."""
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

def migrate():
    conn = engine.connect()
    try:
        print("Starting migration: Making phone_no optional for users...")
        
        # Alter the users table to allow NULL values for phone_no
        conn.execute(text("ALTER TABLE users ALTER COLUMN phone_no DROP NOT NULL"))
        conn.commit()
        
        print("✓ Migration completed successfully!")
        print("  - phone_no is now optional in users table")
        print("  - UNIQUE constraint on phone_no remains active")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

from sqlalchemy import text
from app.core.connectdb import get_connection

migrations = [
    "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS razorpay_order_id varchar",
    "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS razorpay_payment_id varchar",
    "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS payment_status varchar DEFAULT 'PENDING'",
]

conn = get_connection()
try:
    for query in migrations:
        conn.execute(text(query))
        print(f"✓ {query}")
    conn.commit()
    print("Migration completed.")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
finally:
    conn.close()

import os
import hmac
import hashlib
import razorpay
from dotenv import load_dotenv
from sqlalchemy import text
from app.core.connectdb import get_connection

load_dotenv()

client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
)

def create_order(booking_id: str) -> dict:
    conn = get_connection()
    try:
        booking = conn.execute(
            text("""
                SELECT b.booking_id, s.price
                FROM bookings b
                JOIN turf_slots s ON s.slot_id = b.slot_id
                WHERE b.booking_id = :booking_id
            """),
            {"booking_id": booking_id}
        ).fetchone()

        if not booking:
            raise Exception("Booking not found")

        amount_paise = int(float(booking.price) * 100)
        order = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": booking_id,
            "payment_capture": 1
        })

        conn.execute(
            text("UPDATE bookings SET razorpay_order_id = :order_id WHERE booking_id = :booking_id"),
            {"order_id": order["id"], "booking_id": booking_id}
        )
        conn.commit()

        return {
            "order_id": order["id"],
            "amount": amount_paise,
            "currency": "INR",
            "booking_id": booking_id,
            "key": os.getenv("RAZORPAY_KEY_ID")
        }
    finally:
        conn.close()


def verify_payment(data: dict) -> dict:
    booking_id = data.get("booking_id")
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_signature = data.get("razorpay_signature")

    msg = f"{razorpay_order_id}|{razorpay_payment_id}"
    expected = hmac.new(
        os.getenv("RAZORPAY_KEY_SECRET").encode(),
        msg.encode(),
        hashlib.sha256
    ).hexdigest()

    if expected != razorpay_signature:
        raise Exception("Invalid payment signature")

    conn = get_connection()
    try:
        conn.execute(
            text("""
                UPDATE bookings
                SET razorpay_payment_id = :payment_id,
                    payment_status = 'PAID',
                    booking_status = 'CONFIRMED',
                    is_available = false
                WHERE booking_id = :booking_id
            """),
            {"payment_id": razorpay_payment_id, "booking_id": booking_id}
        )
        conn.commit()
        return {"message": "Payment verified and booking confirmed", "booking_id": booking_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

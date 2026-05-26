import os
import hmac
import hashlib
import razorpay
from dotenv import load_dotenv
from sqlalchemy import text
from app.core.connectdb import get_connection

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", RAZORPAY_KEY_SECRET)

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


def create_order(booking_id: str, callback_url: str = None) -> dict:
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

        result = {
            "order_id": order["id"],
            "amount": amount_paise,
            "currency": "INR",
            "booking_id": booking_id,
            "key": RAZORPAY_KEY_ID,
        }

        if callback_url:
            result["callback_url"] = callback_url

        return result
    finally:
        conn.close()


def verify_payment(data: dict) -> dict:
    booking_id = data.get("booking_id")
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_signature = data.get("razorpay_signature")

    print(f"[PAYMENT VERIFY] booking_id={booking_id}")
    print(f"[PAYMENT VERIFY] order_id={razorpay_order_id}")
    print(f"[PAYMENT VERIFY] payment_id={razorpay_payment_id}")
    print(f"[PAYMENT VERIFY] signature={razorpay_signature}")

    msg = f"{razorpay_order_id}|{razorpay_payment_id}"
    expected = hmac.new(
        RAZORPAY_KEY_SECRET.encode(),
        msg.encode(),
        hashlib.sha256
    ).hexdigest()

    print(f"[PAYMENT VERIFY] expected_sig={expected}")
    print(f"[PAYMENT VERIFY] sig_match={expected == razorpay_signature}")

    if expected != razorpay_signature:
        print(f"[PAYMENT VERIFY] SIGNATURE MISMATCH - REJECTING")
        raise Exception("Invalid payment signature")

    print(f"[PAYMENT VERIFY] SIGNATURE VALID - CONFIRMING BOOKING")
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
        print(f"[PAYMENT VERIFY] BOOKING {booking_id} CONFIRMED")
        return {"message": "Payment verified and booking confirmed", "booking_id": booking_id}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def handle_webhook(payload: bytes, signature: str) -> dict:
    """Handle Razorpay webhook events (payment.captured, payment.failed).
    Uses timing-safe comparison to prevent timing attacks.
    """
    expected = hmac.new(
        RAZORPAY_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    # Timing-safe comparison (prevents timing attacks)
    if not hmac.compare_digest(expected, signature):
        raise Exception("Invalid webhook signature")

    import json
    event = json.loads(payload)
    event_type = event.get("event")

    if event_type == "payment.captured":
        payment = event["payload"]["payment"]["entity"]
        order_id = payment.get("order_id")
        payment_id = payment.get("id")

        conn = get_connection()
        try:
            conn.execute(
                text("""
                    UPDATE bookings
                    SET razorpay_payment_id = :payment_id,
                        payment_status = 'PAID',
                        booking_status = 'CONFIRMED',
                        is_available = false
                    WHERE razorpay_order_id = :order_id
                """),
                {"payment_id": payment_id, "order_id": order_id}
            )
            conn.commit()
            return {"status": "ok", "event": event_type}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    elif event_type == "payment.failed":
        payment = event["payload"]["payment"]["entity"]
        order_id = payment.get("order_id")

        conn = get_connection()
        try:
            conn.execute(
                text("""
                    UPDATE bookings
                    SET payment_status = 'FAILED'
                    WHERE razorpay_order_id = :order_id
                """),
                {"order_id": order_id}
            )
            conn.commit()
            return {"status": "ok", "event": event_type}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    return {"status": "ignored", "event": event_type}

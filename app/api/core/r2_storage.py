"""Cloudflare R2 storage service (S3-compatible)."""
import os
import uuid
import boto3
from dotenv import load_dotenv

load_dotenv()

R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL")

s3_client = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT_URL,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name="auto",
)


def upload_file(file_bytes: bytes, filename: str, folder: str, content_type: str = "image/jpeg") -> str:
    """Upload a file to R2 and return the public URL."""
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "jpg"
    key = f"{folder}/{uuid.uuid4().hex}.{ext}"

    s3_client.put_object(
        Bucket=R2_BUCKET_NAME,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )

    return f"{R2_PUBLIC_URL}/{key}"


def delete_file(file_url: str) -> bool:
    """Delete a file from R2 by its public URL."""
    if not file_url or not R2_PUBLIC_URL:
        return False
    key = file_url.replace(f"{R2_PUBLIC_URL}/", "")
    try:
        s3_client.delete_object(Bucket=R2_BUCKET_NAME, Key=key)
        return True
    except Exception:
        return False

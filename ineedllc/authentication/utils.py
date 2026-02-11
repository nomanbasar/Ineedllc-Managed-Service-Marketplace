import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core import signing

def generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"

def otp_expiry(minutes: int = 10):
    return timezone.now() + timedelta(minutes=minutes)

def send_otp_email(email: str, otp: str, purpose: str):
    subject = "Your OTP Code"
    if purpose == "email_verify":
        msg = f"Your signup verification OTP is: {otp}"
    else:
        msg = f"Your password reset OTP is: {otp}"

    send_mail(
        subject=subject,
        message=msg,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

def make_reset_token(user_id: str, email: str) -> str:
    payload = {"user_id": str(user_id), "email": email}
    return signing.dumps(payload, salt="password-reset")

def verify_reset_token(token: str, max_age_seconds: int = 15 * 60):
    return signing.loads(token, salt="password-reset", max_age=max_age_seconds)

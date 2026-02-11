from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from .models import OTP


def enforce_resend_limits(*, user, email, purpose: str, cooldown_seconds: int = 30, max_per_hour: int = 5):
    """
    purpose: "email_verify" অথবা "password_reset"
    - 30s cooldown
    - 1 hour এ max 5
    """

    # Cooldown check
    last_otp = OTP.objects.filter(
        user=user,
        email_address=email,
        purpose=purpose
    ).order_by("-created_at").first()

    if last_otp and (timezone.now() - last_otp.created_at) < timedelta(seconds=cooldown_seconds):
        raise serializers.ValidationError("please_wait_before_resend")

    # Hourly limit
    one_hour_ago = timezone.now() - timedelta(hours=1)
    count_last_hour = OTP.objects.filter(
        user=user,
        email_address=email,
        purpose=purpose,
        created_at__gte=one_hour_ago
    ).count()

    if count_last_hour >= max_per_hour:
        raise serializers.ValidationError("resend_limit_exceeded")


def enforce_otp_attempt_limit(otp_obj, max_attempts: int = 5):
    """
    otp_obj.attempt_count যদি 5+ হয় -> lock
    """
    if otp_obj.attempt_count >= max_attempts:
        raise serializers.ValidationError("too_many_attempts_try_later")


def blacklist_all_refresh_tokens(user):
    """
    Password change/reset হলে user এর সব refresh token blacklist
    """
    for t in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=t)

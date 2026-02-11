from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .security import enforce_resend_limits
from .models import User, OTP, PasswordReset
from .utils import generate_otp, otp_expiry, send_otp_email, make_reset_token, verify_reset_token
from .security import enforce_otp_attempt_limit
from .security import blacklist_all_refresh_tokens

# ---------- SIGNUP (Figma fields) ----------
class SignupSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    email_address = serializers.EmailField()
    user_role = serializers.ChoiceField(choices=[("user","User"), ("provider","Provider")])  # figma: User Role
    password = serializers.CharField(min_length=6, write_only=True)
    confirm_password = serializers.CharField(min_length=6, write_only=True)

    def validate_email_address(self, value):
        if User.objects.filter(email_address=value).exists():
            raise serializers.ValidationError("email_already_exists")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("password_not_match")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email_address=validated_data["email_address"],
            password=validated_data["password"],
            full_name=validated_data["full_name"],
            role=validated_data["user_role"],
        )
        user.is_active = False
        user.is_email_verified = False
        user.save()

        otp_code = generate_otp()
        otp_obj = OTP.objects.create(
            user=user,
            email_address=user.email_address,
            purpose="email_verify",
            otp_code=otp_code,
            expires_at=otp_expiry(10),
        )
        send_otp_email(user.email_address, otp_code, "email_verify")

        return {"email_address": user.email_address, "user_role": user.role, "otp_expires_at": otp_obj.expires_at}

# ---------- EMAIL VERIFY ----------
class VerifyEmailSerializer(serializers.Serializer):
    email_address = serializers.EmailField()
    otp_code = serializers.CharField(min_length=6, max_length=6)

    def create(self, validated_data):
        email = validated_data["email_address"]
        otp_code = validated_data["otp_code"]

        user = User.objects.filter(email_address=email).first()
        if not user:
            raise serializers.ValidationError("user_not_found")

        otp_obj = OTP.objects.filter(
            user=user, email_address=email, purpose="email_verify", is_verified=False
        ).order_by("-created_at").first()

        if not otp_obj:
            raise serializers.ValidationError("otp_not_found")
        if otp_obj.is_expired():
            raise serializers.ValidationError("otp_expired")

        enforce_otp_attempt_limit(otp_obj)

        otp_obj.attempt_count += 1
        otp_obj.save(update_fields=["attempt_count"])

        if otp_obj.otp_code != otp_code:
            raise serializers.ValidationError("invalid_otp")

        otp_obj.is_verified = True
        otp_obj.save(update_fields=["is_verified"])

        user.is_email_verified = True
        user.is_active = True
        user.save(update_fields=["is_email_verified", "is_active"])

        refresh = RefreshToken.for_user(user)
        return {
            "user": {"id": str(user.id), "full_name": user.full_name, "email_address": user.email_address, "role": user.role},
            "tokens": {"access": str(refresh.access_token), "refresh": str(refresh)},
        }

class ResendSignupOtpSerializer(serializers.Serializer):
    email_address = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data["email_address"]
        user = User.objects.filter(email_address=email).first()
        if not user:
            raise serializers.ValidationError("user_not_found")
        if user.is_email_verified:
            raise serializers.ValidationError("email_already_verified")

        enforce_resend_limits(user=user, email=email, purpose="email_verify")

        otp_code = generate_otp()
        otp_obj = OTP.objects.create(
            user=user, email_address=email, purpose="email_verify",
            otp_code=otp_code, expires_at=otp_expiry(10),
        )
        send_otp_email(email, otp_code, "email_verify")
        return {"email_address": email, "otp_expires_at": otp_obj.expires_at}


# ---------- LOGIN ----------
class LoginSerializer(serializers.Serializer):
    email_address = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        email = validated_data["email_address"]
        password = validated_data["password"]

        user = User.objects.filter(email_address=email).first()
        if not user:
            raise serializers.ValidationError("invalid_credentials")
        if not user.is_email_verified or not user.is_active:
            raise serializers.ValidationError("email_not_verified")

        user = authenticate(email_address=email, password=password)
        if user is None:
            raise serializers.ValidationError("invalid_credentials")

        refresh = RefreshToken.for_user(user)
        return {
            "user": {"id": str(user.id), "full_name": user.full_name, "email_address": user.email_address, "role": user.role},
            "tokens": {"access": str(refresh.access_token), "refresh": str(refresh)},
        }

# ---------- FORGOT PASSWORD ----------
class ForgotPasswordSerializer(serializers.Serializer):
    email_address = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data["email_address"]
        user = User.objects.filter(email_address=email).first()
        if not user:
            raise serializers.ValidationError("user_not_found")

        otp_code = generate_otp()
        otp_obj = OTP.objects.create(
            user=user, email_address=email, purpose="password_reset",
            otp_code=otp_code, expires_at=otp_expiry(10),
        )
        send_otp_email(email, otp_code, "password_reset")
        return {"email_address": email, "otp_expires_at": otp_obj.expires_at}

class ResendForgotPasswordOtpSerializer(serializers.Serializer):
    email_address = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data["email_address"]
        user = User.objects.filter(email_address=email).first()
        if not user:
            raise serializers.ValidationError("user_not_found")

        enforce_resend_limits(user=user, email=email, purpose="password_reset")

        otp_code = generate_otp()
        otp_obj = OTP.objects.create(
            user=user, email_address=email, purpose="password_reset",
            otp_code=otp_code, expires_at=otp_expiry(10),
        )
        send_otp_email(email, otp_code, "password_reset")
        return {"email_address": email, "otp_expires_at": otp_obj.expires_at}


# ---------- VERIFY RESET OTP -> returns reset_token ----------
class VerifyResetOtpSerializer(serializers.Serializer):
    email_address = serializers.EmailField()
    otp_code = serializers.CharField(min_length=6, max_length=6)

    def create(self, validated_data):
        email = validated_data["email_address"]
        otp_code = validated_data["otp_code"]

        user = User.objects.filter(email_address=email).first()
        if not user:
            raise serializers.ValidationError("user_not_found")

        otp_obj = OTP.objects.filter(
            user=user,
            email_address=email,
            purpose="password_reset",
            is_verified=False,
        ).order_by("-created_at").first()

        if not otp_obj:
            raise serializers.ValidationError("otp_not_found")
        if otp_obj.is_expired():
            raise serializers.ValidationError("otp_expired")
        
        enforce_otp_attempt_limit(otp_obj)

        otp_obj.attempt_count += 1
        otp_obj.save(update_fields=["attempt_count"])

        if otp_obj.otp_code != otp_code:
            raise serializers.ValidationError("invalid_otp")

        otp_obj.is_verified = True
        otp_obj.save(update_fields=["is_verified"])

        
        refresh = RefreshToken.for_user(user)
        return {
            "accessToken": str(refresh.access_token),
            "refreshToken": str(refresh),
            "user": {
                "email": user.email_address,
                "full_name": user.full_name,
                "role": user.role,
            }
        }


# ---------- RESET PASSWORD (Bearer reset_token in Authorization) ----------
class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=6, write_only=True)
    confirm_password = serializers.CharField(min_length=6, write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("password_not_match")
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        if not user:
            raise serializers.ValidationError("authentication_required")

        # Set new password
        user.set_password(validated_data["new_password"])
        user.save()

        blacklist_all_refresh_tokens(user)


        # Generate fresh tokens after reset
        refresh = RefreshToken.for_user(user)

        return {
            "accessToken": str(refresh.access_token),
            "refreshToken": str(refresh),
            "user": {
                "email": user.email_address,
                "full_name": user.full_name,
                "role": user.role,
            }
        }


# ---------- REFRESH ----------
class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def create(self, validated_data):
        refresh = RefreshToken(validated_data["refresh"])
        return {"access": str(refresh.access_token)}

# ---------- LOGOUT (blacklist refresh) ----------
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def create(self, validated_data):
        token = RefreshToken(validated_data["refresh"])
        token.blacklist()
        return {"message": "logout_success"}

# ---------- CHANGE PASSWORD ----------
class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=6, write_only=True)
    confirm_password = serializers.CharField(min_length=6, write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("password_not_match")
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        if not user:
            raise serializers.ValidationError("authentication_required")

        user.set_password(validated_data["new_password"])
        user.save()

        blacklist_all_refresh_tokens(user)

       
        refresh = RefreshToken.for_user(user)

        return {
           
            "accessToken": str(refresh.access_token),
            "refreshToken": str(refresh),
            "user": {
                "email": user.email_address,
                "full_name": user.full_name,
                "role": user.role,
            }
        }



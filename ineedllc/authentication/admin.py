from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User, OTP, PasswordReset


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("-created_at",)
    list_per_page = 25

    list_display = (
        "avatar_preview",
        "full_name",
        "email_address",
        "role",
        "is_email_verified",
        "is_active",
        "is_staff",
        "created_at",
    )
    list_display_links = ("avatar_preview", "full_name", "email_address")

    search_fields = ("full_name", "email_address")
    list_filter = ("role", "is_active", "is_email_verified", "is_staff", "is_superuser", "created_at")
    date_hierarchy = "created_at"

    readonly_fields = ("id", "created_at", "updated_at", "last_login", "avatar_preview")
    filter_horizontal = ("groups", "user_permissions")

    fieldsets = (
        ("Account", {"fields": ("id", "email_address", "password")}),
        ("Profile", {"fields": ("avatar_preview", "full_name", "role", "profile_image")}),
        ("Status", {"fields": ("is_active", "is_email_verified")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email_address", "full_name", "role", "password1", "password2")}),
    )

    def avatar_preview(self, obj):
        """
        Django 6 safe: always provide args to format_html.
        """
        if getattr(obj, "profile_image", None) and getattr(obj.profile_image, "url", None):
            return format_html(
                '<img src="{}" style="width:32px;height:32px;border-radius:50%;object-fit:cover;" />',
                obj.profile_image.url
            )

        initial = (obj.full_name[:1].upper() if obj.full_name else "U")
        return format_html(
            '<div style="width:32px;height:32px;border-radius:50%;background:#e5e7eb;display:flex;align-items:center;justify-content:center;font-weight:700;color:#374151;">{}</div>',
            initial
        )

    avatar_preview.short_description = "Avatar"


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_per_page = 30

    list_display = (
        "email_address",
        "purpose",
        "otp_code",
        "is_verified",
        "expires_at",
        "attempt_count",
        "resend_count",
        "created_at",
    )
    list_filter = ("purpose", "is_verified", "created_at", "expires_at")
    search_fields = ("email_address", "otp_code", "user__full_name")
    readonly_fields = ("id", "created_at")

    fieldsets = (
        ("OTP Info", {"fields": ("id", "user", "email_address", "purpose", "otp_code")}),
        ("Counters", {"fields": ("attempt_count", "resend_count", "is_verified")}),
        ("Timing", {"fields": ("expires_at", "created_at")}),
    )


@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_per_page = 30

    list_display = (
        "user",
        "user_email",
        "is_used",
        "expires_at",
        "created_at",
    )
    list_filter = ("is_used", "created_at", "expires_at")
    search_fields = ("user__email_address", "user__full_name", "token_hash")
    readonly_fields = ("id", "created_at", "token_hash")

    fieldsets = (
        ("Reset Request", {"fields": ("id", "user", "otp", "token_hash")}),
        ("Status", {"fields": ("is_used", "expires_at", "created_at")}),
    )

    def user_email(self, obj):
        return obj.user.email_address

    user_email.short_description = "Email"

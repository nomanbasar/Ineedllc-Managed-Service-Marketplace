from django.urls import path
from .views import (
    SignupView,
    VerifyEmailView,
    ResendSignupOtpView,
    LoginView,
    ForgotPasswordView,
    VerifyResetOtpView,
    ResetPasswordView,
    ResendForgotPasswordOtpView,
    LogoutView,
    RefreshTokenView,
    ChangePasswordView,
)

urlpatterns = [
    path("signup/", SignupView.as_view()),
    path("verify-email/", VerifyEmailView.as_view()),
    path("resend-signup-otp/", ResendSignupOtpView.as_view()),
    path("login/", LoginView.as_view()),
    path("forgot-password/", ForgotPasswordView.as_view()),
    path("verify-reset-otp/", VerifyResetOtpView.as_view()),
    path("reset-password/", ResetPasswordView.as_view()),
    path("resend-forgot-password-otp/", ResendForgotPasswordOtpView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("refresh-token/", RefreshTokenView.as_view()),
    path("change-password/", ChangePasswordView.as_view()),
]

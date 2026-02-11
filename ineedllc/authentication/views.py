from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from .serializers import (
    SignupSerializer,
    VerifyEmailSerializer,
    ResendSignupOtpSerializer,
    LoginSerializer,
    ForgotPasswordSerializer,
    ResendForgotPasswordOtpSerializer,
    VerifyResetOtpSerializer,
    ResetPasswordSerializer,
    LogoutSerializer,
    RefreshTokenSerializer,
    ChangePasswordSerializer,
)

class SignupView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        s = SignupSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.save()
        return Response({"success": True, "message": "signup_otp_sent", "data": data}, status=status.HTTP_201_CREATED)

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        s = VerifyEmailSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.save()
        return Response({"success": True, "message": "email_verified", "data": data}, status=status.HTTP_200_OK)

class ResendSignupOtpView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        s = ResendSignupOtpSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.save()
        return Response({"success": True, "message": "signup_otp_resent", "data": data}, status=status.HTTP_200_OK)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.save()
        return Response({"success": True, "message": "login_success", "data": data}, status=status.HTTP_200_OK)

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        s = ForgotPasswordSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.save()
        return Response({"success": True, "message": "forgot_password_otp_sent", "data": data}, status=status.HTTP_200_OK)

class ResendForgotPasswordOtpView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        s = ResendForgotPasswordOtpSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.save()
        return Response({"success": True, "message": "forgot_password_otp_resent", "data": data}, status=status.HTTP_200_OK)

class VerifyResetOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = VerifyResetOtpSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.save()

        return Response(
            {
                "success": True,
                "message": "OTP verified",
                **data
            },
            status=status.HTTP_200_OK
        )
    

class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = ResetPasswordSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        data = s.save()

        return Response(
            {
                "success": True,
                "message": "Password reset successful",
                **data
            },
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        
        tokens = OutstandingToken.objects.filter(user=user)

        for t in tokens:
            BlacklistedToken.objects.get_or_create(token=t)

        return Response(
            {
                "success": True,
                "message": "logout_success"
            },
            status=status.HTTP_200_OK
        )

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        s = RefreshTokenSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.save()
        return Response({"success": True, "message": "token_refreshed", "data": data}, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = ChangePasswordSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        data = s.save()

        return Response(
            {
                "success": True,
                "message": "Password changed successfully",
                **data
            },
            status=status.HTTP_200_OK
        )
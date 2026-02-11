from django.contrib.auth.backends import ModelBackend
from .models import User

class EmailBackend(ModelBackend):
    def authenticate(self, request, email_address=None, password=None, **kwargs):
        if email_address is None:
            email_address = kwargs.get("username")

        if not email_address or not password:
            return None

        user = User.objects.filter(email_address=email_address).first()
        if not user:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

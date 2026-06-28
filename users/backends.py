from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()

class PhoneAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        phone = username or kwargs.get('phone')
        if not phone:
            return None
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
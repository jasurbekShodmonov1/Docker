# backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileDataBackend(ModelBackend):
    def authenticate(self, request, bio=None, password=None, **kwargs):
        try:
            # Assume a ForeignKey relationship between CustomUser and Profile
            user = User.objects.get(profile__bio=bio)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

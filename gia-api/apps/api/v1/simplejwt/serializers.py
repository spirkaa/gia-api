from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """TokenObtainPairSerializer with username and email."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["username"] = user.get_username()
        token["email"] = user.email

        return token

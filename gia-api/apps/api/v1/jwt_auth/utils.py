from datetime import datetime

from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import unix_epoch


def jwt_create_payload(user):
    """
    Create JWT claims token.
    To be more standards-compliant please refer to the official JWT standards
    specification: https://tools.ietf.org/html/rfc7519#section-4.1
    """

    issued_at_time = datetime.utcnow()
    expiration_time = issued_at_time + api_settings.JWT_EXPIRATION_DELTA

    payload = {
        "username": user.get_username(),
        "iat": unix_epoch(issued_at_time),
        "exp": expiration_time,
    }

    if api_settings.JWT_PAYLOAD_INCLUDE_USER_ID:
        payload["user_id"] = user.pk

    if hasattr(user, "email"):
        payload["email"] = user.email

    if hasattr(user, "profile"):
        payload["user_profile_id"] = (user.profile.pk if user.profile else None,)

    if api_settings.JWT_ALLOW_REFRESH:
        payload["orig_iat"] = unix_epoch(issued_at_time)

    if api_settings.JWT_AUDIENCE is not None:
        payload["aud"] = api_settings.JWT_AUDIENCE

    if api_settings.JWT_ISSUER is not None:
        payload["iss"] = api_settings.JWT_ISSUER

    return payload

import jwt
from datetime import datetime, timezone

from django.conf import settings

from jwt import (
    ExpiredSignatureError,
    DecodeError,
    InvalidTokenError,
)

from rest_framework.exceptions import AuthenticationFailed


class JWTService:

    @staticmethod
    def generate_access_token(user):
        now = datetime.now(timezone.utc)

        payload = {
            "user_id": str(user.id),
            "email": user.email,
            "type": "access",
            "exp": now + settings.JWT_ACCESS_TOKEN_LIFETIME,
        }
        print("=" * 80)
        print("LOGIN SECRET:", settings.JWT_SECRET_KEY)
        print("LOGIN ALGORITHM:", settings.JWT_ALGORITHM)

        token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        )

        print("GENERATED TOKEN:", token)
        print("=" * 80)
        return token
    
    @staticmethod
    def generate_refresh_token(user):
        now = datetime.now(timezone.utc)

        payload = {
            "user_id": str(user.id),
            "type": "refresh",
            "exp": now + settings.JWT_REFRESH_TOKEN_LIFETIME,
        }

        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @staticmethod
    def decode_token(token):
        try:
            print("VERIFY SECRET:", settings.JWT_SECRET_KEY)
            print("VERIFY ALGORITHM:", settings.JWT_ALGORITHM)
            return jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
          
        except ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired.")

        except DecodeError:
            raise AuthenticationFailed("Invalid token format.")

        except InvalidTokenError:
            raise AuthenticationFailed("Invalid token.")

    @staticmethod
    def verify_access_token(token):
        payload = JWTService.decode_token(token)

        if payload.get("type") != "access":
            raise AuthenticationFailed("Invalid access token.")

        return payload

    @staticmethod
    def verify_refresh_token(token):
        payload = JWTService.decode_token(token)

        if payload.get("type") != "refresh":
            raise AuthenticationFailed("Invalid refresh token.")

        return payload
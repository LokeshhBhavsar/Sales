from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """
    Serializer For User Login
    """
    email = serializers.EmailField(
        required=True,
        max_length=255,
        error_messages = {
            "required": "Email is required",
            "invalid": "Invalid email address",
            "blank": "Email cannot be blank",
        }
        )
    password = serializers.CharField(required=True,
                                     max_length = 128,
                                     write_only=True,
                                     trim_whitespace=True,
                                     error_messages = {
                                         "required": "Password is required",
                                         "blank": "Password cannot be blank",
                                     },
                                     style={'input_type': 'password'}
                                     )
def validate_email(self,value):
    """
     Normalize the email address before passing it to service.
    """
    return value.strip().lower()

def validate_password(self,attrs):
    """
    Normalize the password before passing it to service.
    """
    return attrs.strip()

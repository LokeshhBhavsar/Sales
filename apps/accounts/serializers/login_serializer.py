# from rest_framework import serializers


# class LoginSerializer(serializers.Serializer):
#     """
#     Serializer For User Login
#     """
#     email = serializers.EmailField(
#         required=True,
#         max_length=255,
#         error_messages = {
#             "required": "Email is required",
#             "invalid": "Invalid email address",
#             "blank": "Email cannot be blank",
#         }
#         )
#     password = serializers.CharField(required=True,
#                                      max_length = 128,
#                                      write_only=True,
#                                      trim_whitespace=True,
#                                      error_messages = {
#                                          "required": "Password is required",
#                                          "blank": "Password cannot be blank",
#                                      },
#                                      style={'input_type': 'password'}
#                                      )
# def validate_email(self,value):
#     """
#      Normalize the email address before passing it to service.
#     """
#     return value.strip().lower()

# def validate_password(self,attrs):
#     """
#     Normalize the password before passing it to service.
#     """
#     return attrs.strip()




from rest_framework import serializers
from apps.accounts.models import User


class LoginSerializer(serializers.Serializer):
    """
    Serializer for User Login
    """

    email = serializers.EmailField(
        required=True,
        max_length=255,
        error_messages={
            "required": "Email is required.",
            "invalid": "Invalid email address.",
            "blank": "Email cannot be blank.",
        },
    )

    password = serializers.CharField(
        required=True,
        max_length=128,
        write_only=True,
        trim_whitespace=True,
        error_messages={
            "required": "Password is required.",
            "blank": "Password cannot be blank.",
        },
        style={
            "input_type": "password"
        },
    )

    def validate_email(self, value):
        """
        Normalize email.
        """
        return value.strip().lower()

    def validate_password(self, value):
        """
        Normalize password.
        """
        return value.strip()




 




class LoginUserSerializer(serializers.ModelSerializer):
    """
    Safe user information returned after login.
    """

    company_id = serializers.UUIDField(
        source="company.id",
        read_only=True,
        allow_null=True
    )

    company_name = serializers.CharField(
        source="company.name",
        read_only=True,
        allow_null=True
    )

    plant_id = serializers.UUIDField(
        source="plant.id",
        read_only=True,
        allow_null=True
    )

    plant_name = serializers.CharField(
        source="plant.name",
        read_only=True,
        allow_null=True
    )

    department_id = serializers.UUIDField(
        source="department.id",
        read_only=True,
        allow_null=True
    )

    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
        allow_null=True
    )

    employee_id = serializers.UUIDField(
        source="employee.id",
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = User

        fields = [
            "id",
            "email",
            "first_name",
            "last_name",

            "company_id",
            "company_name",

            "plant_id",
            "plant_name",

            "department_id",
            "department_name",

            "employee_id",

            "is_active",
            "is_staff",
            "is_superuser",
        ]

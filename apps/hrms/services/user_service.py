# # apps/accounts/services/user_service.py

# from django.db import transaction
# from django.contrib.auth import get_user_model

# from rest_framework.exceptions import ValidationError

# from apps.accounts.models.user_role import UserRole


# User = get_user_model()


# class UserService:

#     @staticmethod
#     @transaction.atomic
#     def create_user(validated_data):

#         employee = validated_data["employee"]
#         roles = validated_data["roles"]
#         password = validated_data["password"]

#         # -----------------------------------------
#         # Create User
#         # -----------------------------------------

#         user = User.objects.create_user(
#             email=employee.email,
#             password=password,
#             first_name=employee.first_name,
#             last_name=employee.last_name or "",
#             employee=employee,

#             # -------------------------------------
#             # Copy organizational context
#             # -------------------------------------

#             company=employee.company,
#             plant=employee.plant,
#             department=employee.department,

#             is_active=True,
#         )

#         # -----------------------------------------
#         # Assign Roles
#         # -----------------------------------------

#         user_roles = []

#         for role in roles:

#             user_roles.append(
#                 UserRole(
#                     user=user,
#                     role=role
#                 )
#             )

#         UserRole.objects.bulk_create(
#             user_roles
#         )

#         return user




from django.db import transaction
from django.contrib.auth import get_user_model

from apps.hrms.models.employee import Employee
from apps.accounts.models.user_role import UserRole

User = get_user_model()


class UserService:

    @staticmethod
    @transaction.atomic
    def create_user(validated_data):

        roles = validated_data.pop("roles")
        password = validated_data.pop("password")

        # -----------------------------------------
        # Create Employee
        # -----------------------------------------

        employee = Employee.objects.create(
    employee_code=validated_data["employee_code"],
    first_name=validated_data["first_name"],
    last_name=validated_data.get("last_name", ""),

    company_id=validated_data["company"],
    plant_id=validated_data["plant"],
    department_id=validated_data["department"],

    employment_type=validated_data["employment_type"],
    joining_date=validated_data["joining_date"],
    status=validated_data["status"],

    email=validated_data["email"],
    phone=validated_data.get("phone", ""),
)

        # -----------------------------------------
        # Create User
        # -----------------------------------------

        user = User.objects.create_user(
            email=employee.email,
            password=password,

            first_name=employee.first_name,
            last_name=employee.last_name or "",

            employee=employee,

            # -------------------------------------
            # Organizational context
            # -------------------------------------

            company=employee.company,
            plant=employee.plant,
            department=employee.department,

            is_active=True,
        )

        # -----------------------------------------
        # Assign Roles
        # -----------------------------------------

        user_roles = []

        for role in roles:
            user_roles.append(
                UserRole(
                    user=user,
                    role=role
                )
            )

        UserRole.objects.bulk_create(user_roles)

        return user
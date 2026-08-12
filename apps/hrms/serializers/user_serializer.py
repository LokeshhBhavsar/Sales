# # apps/accounts/serializers/user_serializer.py

# from django.contrib.auth import get_user_model
# from rest_framework import serializers

# from apps.hrms.models.employee import Employee
# from apps.accounts.models.role import Role
# from apps.accounts.models.user_role import UserRole


# User = get_user_model()


# class CreateUserSerializer(serializers.Serializer):

#     employee_id = serializers.UUIDField()

#     password = serializers.CharField(
#         write_only=True,
#         min_length=8
#     )

#     role_ids = serializers.ListField(
#         child=serializers.UUIDField(),
#         required=True,
#         allow_empty=False
#     )

#     def validate(self, attrs):

#         employee_id = attrs["employee_id"]
#         role_ids = attrs["role_ids"]

#         # -----------------------------------------
#         # Employee
#         # -----------------------------------------

#         try:

#             employee = Employee.objects.select_related(
#                 "company",
#                 "plant",
#                 "department"
#             ).get(
#                 id=employee_id,
#                 status="active"
#             )

#         except Employee.DoesNotExist:

#             raise serializers.ValidationError({
#                 "employee_id": "Active employee not found."
#             })

#         # -----------------------------------------
#         # Employee already has User
#         # -----------------------------------------

#         if User.objects.filter(
#             employee=employee
#         ).exists():

#             raise serializers.ValidationError({
#                 "employee_id": "User account already exists for this employee."
#             })

#         # -----------------------------------------
#         # Email
#         # -----------------------------------------

#         if not employee.email:

#             raise serializers.ValidationError({
#                 "employee_id": "Employee does not have an email address."
#             })

#         if User.objects.filter(
#             email__iexact=employee.email
#         ).exists():

#             raise serializers.ValidationError({
#                 "email": "User with this email already exists."
#             })

#         # -----------------------------------------
#         # Roles
#         # -----------------------------------------

#         roles = Role.objects.filter(
#             id__in=role_ids,
#             is_active=True
#         ).select_related(
#             "company",
#             "plant",
#             "department"
#         )

#         if roles.count() != len(set(role_ids)):

#             raise serializers.ValidationError({
#                 "role_ids": "One or more roles are invalid."
#             })

#         # -----------------------------------------
#         # Validate Role Scope
#         # -----------------------------------------

#         for role in roles:

#             # Company Role
#             if role.scope == "company":

#                 if role.company_id != employee.company_id:

#                     raise serializers.ValidationError({
#                         "role_ids": (
#                             f"Role '{role.name}' does not belong "
#                             "to employee's company."
#                         )
#                     })

#             # Plant Role
#             elif role.scope == "plant":

#                 if role.company_id != employee.company_id:

#                     raise serializers.ValidationError({
#                         "role_ids": (
#                             f"Role '{role.name}' does not belong "
#                             "to employee's company."
#                         )
#                     })

#                 if role.plant_id != employee.plant_id:

#                     raise serializers.ValidationError({
#                         "role_ids": (
#                             f"Role '{role.name}' does not belong "
#                             "to employee's plant."
#                         )
#                     })

#             # Department Role
#             elif role.scope == "department":

#                 if role.company_id != employee.company_id:

#                     raise serializers.ValidationError({
#                         "role_ids": (
#                             f"Role '{role.name}' does not belong "
#                             "to employee's company."
#                         )
#                     })

#                 if role.plant_id != employee.plant_id:

#                     raise serializers.ValidationError({
#                         "role_ids": (
#                             f"Role '{role.name}' does not belong "
#                             "to employee's plant."
#                         )
#                     })

#                 if role.department_id != employee.department_id:

#                     raise serializers.ValidationError({
#                         "role_ids": (
#                             f"Role '{role.name}' does not belong "
#                             "to employee's department."
#                         )
#                     })

#         attrs["employee"] = employee
#         attrs["roles"] = list(roles)

#         return attrs




from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from apps.hrms.models.employee import Employee
from apps.accounts.models.role import Role
from apps.accounts.models.user_role import UserRole

User = get_user_model()


class CreateUserSerializer(serializers.Serializer):

    employee_code = serializers.CharField(max_length=50)
    first_name = serializers.CharField(max_length=100)

    last_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    company = serializers.UUIDField()
    plant = serializers.UUIDField()
    department = serializers.UUIDField()


    employment_type = serializers.CharField(max_length=50)
    joining_date = serializers.DateField()
    status = serializers.CharField(max_length=30)

    email = serializers.EmailField()

    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True
    )

    role_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        allow_empty=False
    )

    def validate(self, attrs):

        # Validate employee code
        if Employee.objects.filter(
            employee_code=attrs["employee_code"]
        ).exists():

            raise serializers.ValidationError({
                "employee_code":
                    "Employee with this employee code already exists."
            })

        # Validate email
        if Employee.objects.filter(
            email__iexact=attrs["email"]
        ).exists():

            raise serializers.ValidationError({
                "email":
                    "Employee with this email already exists."
            })

        if User.objects.filter(
            email__iexact=attrs["email"]
        ).exists():

            raise serializers.ValidationError({
                "email":
                    "User with this email already exists."
            })

        # -----------------------------------------
        # Roles
        # -----------------------------------------

        role_ids = attrs["role_ids"]

        roles = Role.objects.filter(
            id__in=role_ids,
            is_active=True
        ).select_related(
            "company",
            "plant",
            "department"
        )

        if roles.count() != len(set(role_ids)):

            raise serializers.ValidationError({
                "role_ids":
                    "One or more roles are invalid."
            })

        # -----------------------------------------
        # Role Scope
        # -----------------------------------------

        for role in roles:

            if role.scope == "company":

                if role.company_id != attrs["company"]:

                    raise serializers.ValidationError({
                        "role_ids":
                            f"Role '{role.name}' does not belong "
                            "to employee's company."
                    })

            elif role.scope == "plant":

                if role.company_id != attrs["company"]:

                    raise serializers.ValidationError({
                        "role_ids":
                            f"Role '{role.name}' does not belong "
                            "to employee's company."
                    })

                if role.plant_id != attrs["plant"]:

                    raise serializers.ValidationError({
                        "role_ids":
                            f"Role '{role.name}' does not belong "
                            "to employee's plant."
                    })

            elif role.scope == "department":

                if role.company_id != attrs["company"]:

                    raise serializers.ValidationError({
                        "role_ids":
                            f"Role '{role.name}' does not belong "
                            "to employee's company."
                    })

                if role.plant_id != attrs["plant"]:

                    raise serializers.ValidationError({
                        "role_ids":
                            f"Role '{role.name}' does not belong "
                            "to employee's plant."
                    })

                if role.department_id != attrs["department"]:

                    raise serializers.ValidationError({
                        "role_ids":
                            f"Role '{role.name}' does not belong "
                            "to employee's department."
                    })

        attrs["roles"] = list(roles)

        return attrs

class UserSerializer(serializers.ModelSerializer):

    employee_id = serializers.UUIDField(
        source="employee.id",
        read_only=True
    )

    employee_code = serializers.CharField(
        source="employee.employee_code",
        read_only=True
    )

    employee_name = serializers.SerializerMethodField()

    company_id = serializers.UUIDField(
        source="company.id",
        read_only=True
    )

    plant_id = serializers.UUIDField(
        source="plant.id",
        read_only=True
    )

    department_id = serializers.UUIDField(
        source="department.id",
        read_only=True
    )

    roles = serializers.SerializerMethodField()

    class Meta:

        model = User

        fields = [
            "id",

            "employee_id",
            "employee_code",
            "employee_name",

            "email",

            "company_id",
            "plant_id",
            "department_id",

            "is_active",

            "roles",
        ]

    def get_employee_name(self, obj):

        if not obj.employee:
            return None

        return (
            f"{obj.employee.first_name} "
            f"{obj.employee.last_name or ''}"
        ).strip()

    def get_roles(self, obj):

        return [
            {
                "id": str(item.role.id),
                "name": item.role.name,
                "code": item.role.code,
                "scope": item.role.scope,
            }
            for item in obj.assigned_roles.select_related(
                "role"
            ).all()
        ]
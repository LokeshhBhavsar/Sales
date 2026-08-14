from django.contrib.auth import get_user_model

from rest_framework import serializers

from apps.hrms.models.employee import Employee
from apps.accounts.models.role import Role


User = get_user_model()


class CreateUserSerializer(serializers.Serializer):

    employee_code = serializers.CharField(
        max_length=50
    )

    first_name = serializers.CharField(
        max_length=100
    )

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

    employment_type = serializers.CharField(
        max_length=50
    )

    joining_date = serializers.DateField()

    status = serializers.CharField(
        max_length=30
    )

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

        request = self.context.get("request")

        if not request:
            raise serializers.ValidationError({
                "request":
                    "Request context is required."
            })

        requesting_user = request.user

        # =====================================================
        # CHECK EMPLOYEE CODE
        # =====================================================

        if Employee.objects.filter(
            employee_code=attrs["employee_code"]
        ).exists():

            raise serializers.ValidationError({
                "employee_code":
                    "Employee with this employee code already exists."
            })

        # =====================================================
        # CHECK EMAIL
        # =====================================================

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

        # =====================================================
        # SUPER ADMIN
        # =====================================================

        is_super_admin = (
            requesting_user.is_superuser
            or
            requesting_user.assigned_roles.filter(
                role__code__iexact="SUPER_ADMIN",
                role__is_active=True
            ).exists()
        )

        # =====================================================
        # PLANT HR / HR MANAGER
        # =====================================================

        is_plant_hr = requesting_user.assigned_roles.filter(
            role__code__in=[
                "PLANT_HR",
                "HR_MANAGER",
            ],
            role__scope="plant",
            role__is_active=True
        ).exists()

        # =====================================================
        # AUTHORIZATION
        # =====================================================

        if not is_super_admin and not is_plant_hr:

            raise serializers.ValidationError({
                "permission":
                    "You are not allowed to create users."
            })

        # =====================================================
        # PLANT HR RESTRICTION
        # =====================================================

        if not is_super_admin:

            # ---------------------------------------------
            # Company
            # ---------------------------------------------

            if str(requesting_user.company_id) != str(
                attrs["company"]
            ):

                raise serializers.ValidationError({
                    "company":
                        "You can only create users "
                        "within your company."
                })

            # ---------------------------------------------
            # Plant
            # ---------------------------------------------

            if str(requesting_user.plant_id) != str(
                attrs["plant"]
            ):

                raise serializers.ValidationError({
                    "plant":
                        "You can only create users "
                        "within your plant."
                })

        # =====================================================
        # ROLES
        # =====================================================

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

        # =====================================================
        # ROLE SCOPE VALIDATION
        # =====================================================

        for role in roles:

            # -------------------------------------------------
            # COMPANY ROLE
            # -------------------------------------------------

            if role.scope == "company":

                if str(role.company_id) != str(
                    attrs["company"]
                ):

                    raise serializers.ValidationError({
                        "role_ids":
                            f"Role '{role.name}' does not belong "
                            "to employee's company."
                    })

            # -------------------------------------------------
            # PLANT ROLE
            # -------------------------------------------------

            elif role.scope == "plant":

                if str(role.company_id) != str(
                    attrs["company"]
                ):

                    raise serializers.ValidationError({
                        "role_ids":
                            f"Role '{role.name}' does not belong "
                            "to employee's company."
                    })

                if str(role.plant_id) != str(
                    attrs["plant"]
                ):

                    raise serializers.ValidationError({
                        "role_ids":
                            f"Role '{role.name}' does not belong "
                            "to employee's plant."
                    })

            # -------------------------------------------------
            # DEPARTMENT ROLE
            # -------------------------------------------------

            elif role.scope == "department":

                if str(role.company_id) != str(
                    attrs["company"]
                ):

                    raise serializers.ValidationError({
                        "role_ids":
                            f"Role '{role.name}' does not belong "
                            "to employee's company."
                    })

                if str(role.plant_id) != str(
                    attrs["plant"]
                ):

                    raise serializers.ValidationError({
                        "role_ids":
                            f"Role '{role.name}' does not belong "
                            "to employee's plant."
                    })

                if str(role.department_id) != str(
                    attrs["department"]
                ):

                    raise serializers.ValidationError({
                        "role_ids":
                            f"Role '{role.name}' does not belong "
                            "to employee's department."
                    })

        # =====================================================
        # PLANT HR CAN ONLY ASSIGN DEPARTMENT ROLES
        # =====================================================

        if not is_super_admin:

            for role in roles:

                if role.scope != "department":

                    raise serializers.ValidationError({
                        "role_ids": (
                            f"Plant HR cannot assign "
                            f"'{role.name}'. Only department-level "
                            "roles can be assigned."
                        )
                    })

        # =====================================================
        # SAVE ROLES FOR SERVICE
        # =====================================================

        attrs["roles"] = list(roles)

        return attrs


# =============================================================
# USER SERIALIZER
# =============================================================

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
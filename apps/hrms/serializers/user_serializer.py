from aiohttp.test_utils import Self
from attr import attrs
from django.contrib.auth import get_user_model

from rest_framework import request, serializers

from apps.accounts.models.user_role import UserRole
from apps.hrms.models.employee import Employee
from apps.accounts.models.role import Role
from apps.hrms.services.user_service import UserService
from apps.masters.models.company import Company
from apps.masters.models.plant import Plant
from apps.masters.models.department import Department
from apps.accounts.services.password_encryption_service import (
    PasswordEncryptionService
)


User = get_user_model()

from uuid import UUID

from django.db import transaction
from rest_framework import serializers

from apps.hrms.models.employee import Employee

from apps.hrms.services.user_service import UserService


class CreateUserSerializer(serializers.Serializer):

    employee_code = serializers.CharField(
        max_length=50
    )

    username = serializers.CharField(
        max_length=100
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
        min_length=8,
        required=False,
        allow_blank=True
    )

    # ---------------------------------------------------------
    # COMPANY
    # ---------------------------------------------------------

    company = serializers.UUIDField(
        required=True
    )

    # ---------------------------------------------------------
    # PLANT
    # Accept UUID OR ""
    # ---------------------------------------------------------

    plant = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    # ---------------------------------------------------------
    # DEPARTMENT
    # Accept UUID OR ""
    # ---------------------------------------------------------

    department = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    employment_type = serializers.CharField(
        max_length=50
    )

    joining_date = serializers.DateField()

    status = serializers.CharField(
        max_length=30
    )

    email = serializers.EmailField(
    required=False,
    allow_blank=True,
    allow_null=True
)

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

    # =========================================================
    # VALIDATE
    # =========================================================

    def validate(self, attrs):

        request = self.context.get("request")

        if not request:
            raise serializers.ValidationError({
                "request":
                    "Request context is required."
            })

        requesting_user = request.user

        # =====================================================
        # NORMALIZE PLANT
        # =====================================================

        plant = attrs.get("plant")

        if plant in ("", None):
            plant = None

        else:
            try:
                plant = UUID(str(plant))
            except (ValueError, TypeError, AttributeError):

                raise serializers.ValidationError({
                    "plant":
                        "Invalid plant UUID."
                })

        # =====================================================
        # NORMALIZE DEPARTMENT
        # =====================================================

        department = attrs.get("department")

        if department in ("", None):
            department = None

        else:
            try:
                department = UUID(str(department))
            except (ValueError, TypeError, AttributeError):

                raise serializers.ValidationError({
                    "department":
                        "Invalid department UUID."
                })

        attrs["plant"] = plant
        attrs["department"] = department
        # =====================================================
# CHECK USERNAME
# =====================================================

        if Employee.objects.filter(
            username__iexact=attrs["username"]
            ).exists():

            raise serializers.ValidationError({
                "username":
                "Employee with this username already exists."
         })

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

        # =====================================================
# CHECK EMAIL
# =====================================================

        email = attrs.get("email")

        if email:
            if Employee.objects.filter(
            email__iexact=email
        ).exists():

                raise serializers.ValidationError({
                "email":
                "Employee with this email already exists."
            })

            if User.objects.filter(
                email__iexact=email
            ).exists():

                raise serializers.ValidationError({
                "email":
                "User with this email already exists."
        })

        # # =====================================================
        # # CHECK SUPER ADMIN
        # # =====================================================

        # is_super_admin = UserService.is_super_admin(
        #     requesting_user
        # )

        # # =====================================================
        # # CHECK PLANT HR
        # # =====================================================

        # is_plant_hr = requesting_user.assigned_roles.filter(
        #     role__code__in=[
        #         "PLANT_HR",
        #         "HR_MANAGER",
        #     ],
        #     role__scope="plant",
        #     role__is_active=True
        # ).exists()

        # # =====================================================
        # # AUTHORIZATION
        # # =====================================================

        # if not is_super_admin and not is_plant_hr:

        #     raise serializers.ValidationError({
        #         "permission":
        #             "You are not allowed to create users."
        #     })
        # =====================================================
# # CHECK SUPER ADMIN
# # =====================================================

#         is_super_admin = UserService.is_super_admin(
#             requesting_user
#         )

# # =====================================================
# # CHECK PLANT HR
# # =====================================================

#         is_plant_hr = requesting_user.assigned_roles.filter(
#         role__code__in=[
#             "PLANT_HR",
#             "HR_MANAGER",
#         ],
#         role__scope="plant",
#         role__is_active=True
#     ).exists()

# # =====================================================
# # AUTHORIZATION
# # =====================================================

#         if not is_super_admin and not is_plant_hr:

#             raise serializers.ValidationError({
#             "permission":
#             "You are not allowed to create users."
#     })
        # =====================================================
        # PLANT HR RESTRICTION
        # =====================================================

        # if not is_super_admin:

        #     # -------------------------------------------------
        #     # COMPANY
        #     # -------------------------------------------------

        #     if (
        #         not requesting_user.company_id
        #         or
        #         str(requesting_user.company_id)
        #         != str(attrs["company"])
        #     ):

        #         raise serializers.ValidationError({
        #             "company":
        #                 "You can only create users "
        #                 "within your company."
        #         })

        #     # -------------------------------------------------
        #     # PLANT
        #     # -------------------------------------------------

        #     if not requesting_user.plant_id:

        #         raise serializers.ValidationError({
        #             "plant":
        #                 "Your account is not assigned to a plant."
        #         })

        #     if not plant:

        #         raise serializers.ValidationError({
        #             "plant":
        #                 "Plant is required for Plant HR "
        #                 "user creation."
        #         })

        #     if (
        #         str(requesting_user.plant_id)
        #         != str(plant)
        #     ):

        #         raise serializers.ValidationError({
        #             "plant":
        #                 "You can only create users "
        #                 "within your plant."
        #         })

        # =====================================================
        # FETCH ROLES
        # =====================================================

        role_ids = attrs["role_ids"]

        roles = list(
            Role.objects
            .filter(
                id__in=role_ids,
                is_active=True
            )
            .select_related(
                "company",
                "plant",
                "department"
            )
        )

        # =====================================================
        # VALIDATE ROLE COUNT
        # =====================================================

        if len(roles) != len(set(role_ids)):

            raise serializers.ValidationError({
                "role_ids":
                    "One or more roles are invalid."
            })

        # =====================================================
        # DETERMINE REQUIRED SCOPE
        # =====================================================

        scopes = {
            role.scope
            for role in roles
        }

        # =====================================================
        # COMPANY LEVEL ROLE
        # =====================================================

        if "company" in scopes:

            if not attrs.get("company"):

                raise serializers.ValidationError({
                    "company":
                        "Company is required for "
                        "company-level roles."
                })

        # =====================================================
        # PLANT LEVEL ROLE
        # =====================================================

        if "plant" in scopes:

            if not plant:

                raise serializers.ValidationError({
                    "plant":
                        "Plant is required for "
                        "plant-level roles."
                })

        # =====================================================
        # DEPARTMENT LEVEL ROLE
        # =====================================================

        # if "department" in scopes:

        #     if not plant:

        #         raise serializers.ValidationError({
        #             "plant":
        #                 "Plant is required for "
        #                 "department-level roles."
        #         })

        #     if not department:

        #         raise serializers.ValidationError({
        #             "department":
        #                 "Department is required for "
        #                 "department-level roles."
        #         })

        # =====================================================
        # VALIDATE EACH ROLE
        # =====================================================

        for role in roles:

            # -------------------------------------------------
            # COMPANY ROLE
            # -------------------------------------------------

            if role.scope == "company":

                if (
                    str(role.company_id)
                    != str(attrs["company"])
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

                if (
                    str(role.company_id)
                    != str(attrs["company"])
                ):

                    raise serializers.ValidationError({
                        "role_ids":
                            f"Role '{role.name}' does not belong "
                            "to employee's company."
                    })

                if not plant:

                    raise serializers.ValidationError({
                        "plant":
                            f"Plant is required for "
                            f"role '{role.name}'."
                    })

                if (
                    str(role.plant_id)
                    != str(plant)
                ):

                    raise serializers.ValidationError({
                        "role_ids":
                            f"Role '{role.name}' does not belong "
                            "to employee's plant."
                    })

            # # -------------------------------------------------
            # # DEPARTMENT ROLE
            # # -------------------------------------------------

            # elif role.scope == "department":

            #     if (
            #         str(role.company_id)
            #         != str(attrs["company"])
            #     ):

            #         raise serializers.ValidationError({
            #             "role_ids":
            #                 f"Role '{role.name}' does not belong "
            #                 "to employee's company."
            #         })

            #     if not plant:

            #         raise serializers.ValidationError({
            #             "plant":
            #                 f"Plant is required for "
            #                 f"role '{role.name}'."
            #         })

            #     if (
            #         str(role.plant_id)
            #         != str(plant)
            #     ):

            #         raise serializers.ValidationError({
            #             "role_ids":
            #                 f"Role '{role.name}' does not belong "
            #                 "to employee's plant."
            #         })

            #     if not department:

            #         raise serializers.ValidationError({
            #             "department":
            #                 f"Department is required for "
            #                 f"role '{role.name}'."
            #         })

            #     if (
            #         str(role.department_id)
            #         != str(department)
            #     ):

            #         raise serializers.ValidationError({
            #             "role_ids":
            #                 f"Role '{role.name}' does not belong "
            #                 "to employee's department."
            #         })

        # # =====================================================
        # # PLANT HR CAN ONLY ASSIGN DEPARTMENT ROLES
        # # =====================================================

        # if not is_super_admin:

        #     for role in roles:

        #         if role.scope != "department":

        #             raise serializers.ValidationError({
        #                 "role_ids": (
        #                     f"Plant HR cannot assign "
        #                     f"'{role.name}'. "
        #                     "Only department-level roles "
        #                     "can be assigned."
        #                 )
        #             })
    #         # -------------------------------------------------
    # # UNSUPPORTED ROLE SCOPE
    # # -------------------------------------------------

    #         else:

    #             raise serializers.ValidationError({
    #                 "role_ids": (
    #                     f"Role '{role.name}' uses unsupported "
    #                     f"scope '{role.scope}'. "
    #                     "Only company and plant roles are "
    #                     "allowed for user creation."
    #                 )
    #             })
                # =====================================================
        # SAVE ROLES FOR SERVICE
        # =====================================================

        attrs["roles"] = roles

        return attrs

    # =========================================================
    # CREATE USER
    # =========================================================

    @staticmethod
    @transaction.atomic
    def create_user(validated_data):

        roles = validated_data.pop("roles")
        password = validated_data.pop("password")

        # -----------------------------------------------------
        # Optional organization values
        # -----------------------------------------------------

        company_id = validated_data["company"]

        plant_id = validated_data.get("plant")
        department_id = validated_data.get("department")

        # -----------------------------------------------------
        # Create Employee
        # -----------------------------------------------------

        employee = Employee.objects.create(
            employee_code=validated_data["employee_code"],

            first_name=validated_data["first_name"],

            last_name=validated_data.get(
                "last_name",
                ""
            ),

            company_id=company_id,

            plant_id=plant_id,

            department_id=department_id,

            employment_type=validated_data[
                "employment_type"
            ],

            joining_date=validated_data[
                "joining_date"
            ],

            status=validated_data[
                "status"
            ],

            email=validated_data[
                "email"
            ],

            phone=validated_data.get(
                "phone",
                ""
            ),
        )

        # -----------------------------------------------------
        # Create User
        # -----------------------------------------------------

        user = User.objects.create_user(
            email=employee.email,

            password=password,

            first_name=employee.first_name,

            last_name=employee.last_name or "",

            employee=employee,

            company=employee.company,

            plant=employee.plant,

            department=employee.department,

            is_active=True,
        )

        # -----------------------------------------------------
        # Assign Roles
        # -----------------------------------------------------

        user_roles = [
            UserRole(
                user=user,
                role=role
            )
            for role in roles
        ]

        UserRole.objects.bulk_create(
            user_roles
        )

        return user

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

# class UserListSerializer(serializers.ModelSerializer):

#     company_id = serializers.SerializerMethodField()
#     company_name = serializers.SerializerMethodField()

#     plant_id = serializers.SerializerMethodField()
#     plant_name = serializers.SerializerMethodField()

#     department_id = serializers.SerializerMethodField()
#     department_name = serializers.SerializerMethodField()

#     roles = serializers.SerializerMethodField()

#     class Meta:
#         model = User

#         fields = [
#             "id",

#             "email",
#             "first_name",
#             "last_name",

#             "company_id",
#             "company_name",

#             "plant_id",
#             "plant_name",

#             "department_id",
#             "department_name",

#             "roles",

#             "is_active",
#             "is_staff",
#             "is_superuser",
#         ]

#     def get_company_id(self, obj):

#         return (
#             str(obj.company.id)
#             if obj.company
#             else None
#         )

#     def get_company_name(self, obj):

#         return (
#             obj.company.name
#             if obj.company
#             else None
#         )

#     def get_plant_id(self, obj):

#         return (
#             str(obj.plant.id)
#             if obj.plant
#             else None
#         )

#     def get_plant_name(self, obj):

#         return (
#             obj.plant.name
#             if obj.plant
#             else None
#         )

#     def get_department_id(self, obj):

#         return (
#             str(obj.department.id)
#             if obj.department
#             else None
#         )

#     def get_department_name(self, obj):

#         return (
#             obj.department.name
#             if obj.department
#             else None
#         )

#     def get_roles(self, obj):

#         return [
#             {
#                 "id": str(item.role.id),
#                 "name": item.role.name,
#                 "code": item.role.code,
#                 "scope": item.role.scope,
#             }
#             for item in obj.assigned_roles.select_related(
#                 "role"
#             ).all()
#         ]

# =============================================================
# USER UPDATE SERIALIZER
# =============================================================

class UserUpdateSerializer(serializers.Serializer):

    # ---------------------------------------------------------
    # USER FIELDS
    # ---------------------------------------------------------

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    first_name = serializers.CharField(
        max_length=100,
        required=False
    )

    last_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True
    )

    is_active = serializers.BooleanField(
        required=False
    )

    # ---------------------------------------------------------
    # EMPLOYEE FIELDS
    # ---------------------------------------------------------

    employee_code = serializers.CharField(
        max_length=50,
        required=False
    )

    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        allow_null=True
    )

    employment_type = serializers.CharField(
        max_length=50,
        required=False
    )

    joining_date = serializers.DateField(
        required=False,
        allow_null=True
    )

    status = serializers.CharField(
        max_length=30,
        required=False
    )

    # ---------------------------------------------------------
    # ORGANIZATION
    # ---------------------------------------------------------

    company = serializers.UUIDField(
        required=False,
        allow_null=True
    )

    plant = serializers.UUIDField(
        required=False,
        allow_null=True
    )

    department = serializers.UUIDField(
        required=False,
        allow_null=True
    )

    # ---------------------------------------------------------
    # ROLES
    # ---------------------------------------------------------

    role_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True
    )

    # =========================================================
    # VALIDATE
    # =========================================================

    def validate(self, attrs):

        user = self.instance

        employee = user.employee

        # -----------------------------------------------------
        # EMAIL
        # -----------------------------------------------------

        if "email" in attrs:

            email = attrs["email"]

            if email:

                if User.objects.filter(
                    email__iexact=email
                ).exclude(
                    id=user.id
                ).exists():

                    raise serializers.ValidationError({
                        "email":
                            "User with this email already exists."
                    })

                if Employee.objects.filter(
                    email__iexact=email
                ).exclude(
                    id=employee.id if employee else None
                ).exists():

                    raise serializers.ValidationError({
                        "email":
                            "Employee with this email already exists."
                    })

        # -----------------------------------------------------
        # EMPLOYEE CODE
        # -----------------------------------------------------

        if employee and "employee_code" in attrs:

            employee_code = attrs["employee_code"]

            if Employee.objects.filter(
                employee_code=employee_code
            ).exclude(
                id=employee.id
            ).exists():

                raise serializers.ValidationError({
                    "employee_code":
                        "Employee with this employee code already exists."
                })

        # -----------------------------------------------------
        # ORGANIZATION
        # -----------------------------------------------------

        company_id = attrs.get(
            "company",
            user.company_id
        )

        plant_id = attrs.get(
            "plant",
            user.plant_id
        )

        department_id = attrs.get(
            "department",
            user.department_id
        )

        # -----------------------------------------------------
        # COMPANY
        # -----------------------------------------------------

        company = None

        if company_id:

            try:
                company = Company.objects.get(
                    id=company_id
                )

            except Company.DoesNotExist:

                raise serializers.ValidationError({
                    "company":
                        "Company not found."
                })

        # -----------------------------------------------------
        # PLANT
        # -----------------------------------------------------

        plant = None

        if plant_id:

            try:
                plant = Plant.objects.get(
                    id=plant_id,
                    company=company
                )

            except Plant.DoesNotExist:

                raise serializers.ValidationError({
                    "plant":
                        "Plant does not belong to selected company."
                })

        # -----------------------------------------------------
        # DEPARTMENT
        # -----------------------------------------------------

        department = None

        if department_id:

            try:
                department = Department.objects.get(
                    id=department_id,
                    plant=plant
                )

            except Department.DoesNotExist:

                raise serializers.ValidationError({
                    "department":
                        "Department does not belong to selected plant."
                })

        attrs["company"] = company
        attrs["plant"] = plant
        attrs["department"] = department

        # -----------------------------------------------------
        # ROLE VALIDATION
        # -----------------------------------------------------

        if "role_ids" in attrs:

            role_ids = attrs["role_ids"]

            roles = list(
                Role.objects.filter(
                    id__in=role_ids,
                    is_active=True
                )
            )

            if len(roles) != len(set(role_ids)):

                raise serializers.ValidationError({
                    "role_ids":
                        "One or more roles are invalid."
                })
            
            # =====================================================
# DEPARTMENT SCOPE DISABLED
# =====================================================

            department_roles = [
                role.name
                for role in roles
                if role.scope == "department"
        ]

            if department_roles:

                raise serializers.ValidationError({
                    "role_ids": (
                    "Department-level roles are not allowed "
                    "for user creation."
            )
        })

            for role in roles:

                if role.scope == "company":

                    if (
                        role.company_id != company.id
                        if company
                        else True
                    ):

                        raise serializers.ValidationError({
                            "role_ids":
                                f"Role '{role.name}' "
                                "does not belong to selected company."
                        })

                elif role.scope == "plant":

                    if not plant:

                        raise serializers.ValidationError({
                            "plant":
                                f"Plant is required for role "
                                f"'{role.name}'."
                        })

                    if (
                        role.company_id != company.id
                        or role.plant_id != plant.id
                    ):

                        raise serializers.ValidationError({
                            "role_ids":
                                f"Role '{role.name}' "
                                "does not belong to selected plant."
                        })

                elif role.scope == "department":

                    if not department:

                        raise serializers.ValidationError({
                            "department":
                                f"Department is required for role "
                                f"'{role.name}'."
                        })

                    if (
                        role.company_id != company.id
                        or role.plant_id != plant.id
                        or role.department_id != department.id
                    ):

                        raise serializers.ValidationError({
                            "role_ids":
                                f"Role '{role.name}' "
                                "does not belong to selected department."
                        })

            attrs["roles"] = roles

        return attrs

class UserListSerializer(serializers.ModelSerializer):

    # =====================================================
    # COMPANY
    # =====================================================

    company_id = serializers.UUIDField(
        source="company.id",
        read_only=True,
        allow_null=True,
    )

    company_name = serializers.CharField(
        source="company.name",
        read_only=True,
        allow_null=True,
    )

    # =====================================================
    # PLANT
    # =====================================================

    plant_id = serializers.UUIDField(
        source="plant.id",
        read_only=True,
        allow_null=True,
    )

    plant_name = serializers.CharField(
        source="plant.name",
        read_only=True,
        allow_null=True,
    )

    # =====================================================
    # DEPARTMENT
    # =====================================================

    department_id = serializers.UUIDField(
        source="department.id",
        read_only=True,
        allow_null=True,
    )

    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
        allow_null=True,
    )

    # =====================================================
    # EMPLOYEE
    # =====================================================

    employee_id = serializers.UUIDField(
        source="employee.id",
        read_only=True,
        allow_null=True,
    )

    employee_code = serializers.CharField(
        source="employee.employee_code",
        read_only=True,
        allow_null=True,
    )

    employee_name = serializers.SerializerMethodField()

    # =====================================================
    # ROLES
    # =====================================================

    roles = serializers.SerializerMethodField()

    # =====================================================
    # FULL NAME
    # =====================================================

    full_name = serializers.SerializerMethodField()

    # =====================================================
    # META
    # =====================================================
    password_recovery = serializers.SerializerMethodField()
    class Meta:

        model = User

        fields = [
            # ---------------------------------------------
            # USER
            # ---------------------------------------------

            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",

            # ---------------------------------------------
            # EMPLOYEE
            # ---------------------------------------------

            "employee_id",
            "employee_code",
            "employee_name",

            # ---------------------------------------------
            # COMPANY
            # ---------------------------------------------

            "company_id",
            "company_name",

            # ---------------------------------------------
            # PLANT
            # ---------------------------------------------

            "plant_id",
            "plant_name",

            # ---------------------------------------------
            # DEPARTMENT
            # ---------------------------------------------

            "department_id",
            "department_name",

            # ---------------------------------------------
            # ROLES
            # ---------------------------------------------

            "roles",
            "password_recovery",

            # ---------------------------------------------
            # STATUS
            # ---------------------------------------------

            "is_active",
            "is_staff",
            "is_superuser",
        ]

    # =====================================================
    # FULL NAME
    # =====================================================

    def get_full_name(self, obj):

        name = f"{obj.first_name or ''} {obj.last_name or ''}"

        return name.strip()

    # =====================================================
    # EMPLOYEE NAME
    # =====================================================

    def get_employee_name(self, obj):

        if not obj.employee:
            return None

        name = (
            f"{obj.employee.first_name or ''} "
            f"{obj.employee.last_name or ''}"
        )

        return name.strip()

    # =====================================================
    # ROLES
    # =====================================================

    def get_roles(self, obj):

        roles = []

        for user_role in obj.assigned_roles.all():

            role = user_role.role

            if not role:
                continue

            roles.append({
                "id": str(role.id),
                "name": role.name,
                "code": role.code,
                "scope": getattr(
                    role,
                    "scope",
                    None
                ),
                "is_active": getattr(
                    role,
                    "is_active",
                    True
                ),
            })

        return roles
    
            # =====================================================
    # PASSWORD RECOVERY
    # =====================================================

    def get_password_recovery(self, obj):

        if not obj.encrypted_password:
            return None

        try:

            return PasswordEncryptionService.decrypt(
                obj.encrypted_password
            )

        except Exception:

            return None
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




# from django.db import transaction
# from django.contrib.auth import get_user_model

# from apps.hrms.models.employee import Employee
# from apps.accounts.models.user_role import UserRole

# User = get_user_model()


# class UserService:

#     @staticmethod
#     @transaction.atomic
#     def create_user(validated_data):

#         roles = validated_data.pop("roles")
#         password = validated_data.pop("password")

#         # -----------------------------------------
#         # Create Employee
#         # -----------------------------------------

#         employee = Employee.objects.create(
#     employee_code=validated_data["employee_code"],
#     first_name=validated_data["first_name"],
#     last_name=validated_data.get("last_name", ""),

#     company_id=validated_data["company"],
#     plant_id=validated_data["plant"],
#     department_id=validated_data["department"],

#     employment_type=validated_data["employment_type"],
#     joining_date=validated_data["joining_date"],
#     status=validated_data["status"],

#     email=validated_data["email"],
#     phone=validated_data.get("phone", ""),
# )

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
#             # Organizational context
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

#         UserRole.objects.bulk_create(user_roles)

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

    # =========================================================
    # GET USER ROLES
    # =========================================================

    @staticmethod
    def get_user_roles(user):

        return list(
            UserRole.objects
            .filter(user=user)
            .select_related("role")
        )

    # =========================================================
    # CHECK SUPER ADMIN
    # =========================================================

    @staticmethod
    def is_super_admin(user):

        if user.is_superuser:
            return True

        roles = UserService.get_user_roles(user)

        role_names = {
            item.role.name.strip().upper()
            for item in roles
            if item.role
        }

        role_codes = {
            item.role.code.strip().upper()
            for item in roles
            if item.role and item.role.code
        }

        return bool(
            role_names.intersection({
                "SA",
                "SUPER ADMIN",
                "SUPER_ADMIN",
                "SUPERADMIN",
            })
            or
            role_codes.intersection({
                "SA",
                "SUPER_ADMIN",
                "SUPERADMIN",
            })
        )

    # =========================================================
    # CHECK HR
    # =========================================================

    @staticmethod
    def is_hr(user):

        roles = UserService.get_user_roles(user)

        role_names = {
            item.role.name.strip().upper()
            for item in roles
            if item.role
        }

        role_codes = {
            item.role.code.strip().upper()
            for item in roles
            if item.role and item.role.code
        }

        return bool(
            role_names.intersection({
                "HR",
                "HR MANAGER",
                "HR_MANAGER",
                "PLANT HR",
                "PLANT_HR",
            })
            or
            role_codes.intersection({
                "HR",
                "HR_MANAGER",
                "PLANT_HR",
            })
        )

    # =========================================================
    # GET USERS
    # =========================================================

    @staticmethod
    def get_users(
        logged_in_user,
        company_id=None,
        plant_id=None,
        department_id=None,
    ):

        queryset = (
            User.objects
            .select_related(
                "employee",
                "company",
                "plant",
                "department",
            )
            .prefetch_related(
                "assigned_roles__role"
            )
        )

        # =====================================================
        # SUPER ADMIN
        # =====================================================

        if UserService.is_super_admin(logged_in_user):

            # SA must have company
            if not logged_in_user.company_id:
                return User.objects.none()

            # SA can only see users
            # from his company
            queryset = queryset.filter(
                company_id=logged_in_user.company_id
            )

            # -----------------------------------------
            # Company filter
            # -----------------------------------------

            if company_id:

                # Don't allow SA to access
                # another company

                if str(company_id) != str(
                    logged_in_user.company_id
                ):
                    return User.objects.none()

                queryset = queryset.filter(
                    company_id=company_id
                )

            # -----------------------------------------
            # Plant filter
            # -----------------------------------------

            if plant_id:
                queryset = queryset.filter(
                    plant_id=plant_id
                )

            # -----------------------------------------
            # Department filter
            # -----------------------------------------

            if department_id:
                queryset = queryset.filter(
                    department_id=department_id
                )

            return queryset.order_by(
                "first_name",
                "last_name",
            )

        # =====================================================
        # HR
        # =====================================================

        if UserService.is_hr(logged_in_user):

            # HR must have company
            if not logged_in_user.company_id:
                return User.objects.none()

            # HR must have plant
            if not logged_in_user.plant_id:
                return User.objects.none()

            # -----------------------------------------
            # HR can ONLY see own company + own plant
            # -----------------------------------------

            queryset = queryset.filter(
                company_id=logged_in_user.company_id,
                plant_id=logged_in_user.plant_id,
            )

            # -----------------------------------------
            # Company filter
            # -----------------------------------------

            if company_id:

                if str(company_id) != str(
                    logged_in_user.company_id
                ):
                    return User.objects.none()

                queryset = queryset.filter(
                    company_id=company_id
                )

            # -----------------------------------------
            # Plant filter
            # -----------------------------------------

            if plant_id:

                if str(plant_id) != str(
                    logged_in_user.plant_id
                ):
                    return User.objects.none()

                queryset = queryset.filter(
                    plant_id=plant_id
                )

            # -----------------------------------------
            # Department filter
            # -----------------------------------------

            if department_id:
                queryset = queryset.filter(
                    department_id=department_id
                )

            return queryset.order_by(
                "first_name",
                "last_name",
            )

        # =====================================================
        # OTHER USERS
        # =====================================================

        return User.objects.none()

    # =========================================================
    # GET USER BY ID
    # =========================================================

    @staticmethod
    def get_user_by_id(
        logged_in_user,
        user_id,
    ):

        try:

            user = (
                User.objects
                .select_related(
                    "employee",
                    "company",
                    "plant",
                    "department",
                )
                .prefetch_related(
                    "assigned_roles__role"
                )
                .get(
                    id=user_id
                )
            )

        except User.DoesNotExist:

            return None

        # =====================================================
        # SUPER ADMIN
        # =====================================================

        if UserService.is_super_admin(logged_in_user):

            if not logged_in_user.company_id:
                return None

            if user.company_id != logged_in_user.company_id:
                return None

            return user

        # =====================================================
        # HR
        # =====================================================

        if UserService.is_hr(logged_in_user):

            if not logged_in_user.company_id:
                return None

            if not logged_in_user.plant_id:
                return None

            # Same company
            if user.company_id != logged_in_user.company_id:
                return None

            # Same plant
            if user.plant_id != logged_in_user.plant_id:
                return None

            return user

        # =====================================================
        # OTHER USERS
        # =====================================================

        return None
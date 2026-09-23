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
from django.db.models import Q

from apps.hrms.models.employee import Employee
from apps.accounts.models.user_role import UserRole

User = get_user_model()


class UserService:

    # @staticmethod
    # @transaction.atomic
    # def create_user(validated_data):

    #     roles = validated_data.pop("roles")
    #     password = validated_data.pop("password")

    #     # -----------------------------------------
    #     # Create Employee
    #     # -----------------------------------------

    #     employee = Employee.objects.create(
    #         employee_code=validated_data["employee_code"],
    #         first_name=validated_data["first_name"],
    #         last_name=validated_data.get("last_name", ""),

    #         company_id=validated_data["company"],
    #         plant_id=validated_data["plant"],
    #         department_id=validated_data["department"],

    #         employment_type=validated_data["employment_type"],
    #         joining_date=validated_data["joining_date"],
    #         status=validated_data["status"],

    #         email=validated_data["email"],
    #         phone=validated_data.get("phone", ""),
    #     )

    #     # -----------------------------------------
    #     # Create User
    #     # -----------------------------------------

    #     user = User.objects.create_user(
    #         email=employee.email,
    #         password=password,

    #         first_name=employee.first_name,
    #         last_name=employee.last_name or "",

    #         employee=employee,

    #         # -------------------------------------
    #         # Organizational context
    #         # -------------------------------------

    #         company=employee.company,
    #         plant=employee.plant,
    #         department=employee.department,

    #         is_active=True,
    #     )

    #     # -----------------------------------------
    #     # Assign Roles
    #     # -----------------------------------------

    #     user_roles = []

    #     for role in roles:
    #         user_roles.append(
    #             UserRole(
    #                 user=user,
    #                 role=role
    #             )
    #         )

    #     UserRole.objects.bulk_create(user_roles)

    #     return user

    @staticmethod
    @transaction.atomic
    def create_user(validated_data):

        roles = validated_data.pop("roles")
        password = validated_data.pop("password")

        company_id = validated_data["company"]

        plant_id = validated_data.get("plant")
        department_id = validated_data.get("department")

        # Empty string protection
        if plant_id == "":
            plant_id = None

        if department_id == "":
            department_id = None

        # -----------------------------------------
        # Create Employee
        # -----------------------------------------

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

            status=validated_data["status"],

            email=validated_data["email"],

            phone=validated_data.get(
                "phone",
                ""
            ),
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

            company=employee.company,

            plant=employee.plant,

            department=employee.department,

            is_active=True,
        )

        # -----------------------------------------
        # Assign Roles
        # -----------------------------------------

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

    # @staticmethod
    # def get_users(
    #     logged_in_user,
    #     company_id=None,
    #     plant_id=None,
    #     department_id=None,
    # ):

    #     queryset = (
    #         User.objects
    #         .select_related(
    #             "employee",
    #             "company",
    #             "plant",
    #             "department",
    #         )
    #         .prefetch_related(
    #             "assigned_roles__role"
    #         )
    #     )

    #     # =====================================================
    #     # SUPER ADMIN
    #     # =====================================================

    #     if UserService.is_super_admin(logged_in_user):

    #         # SA must have company
    #         if not logged_in_user.company_id:
    #             return User.objects.none()

    #         # SA can only see users
    #         # from his company
    #         queryset = queryset.filter(
    #             company_id=logged_in_user.company_id
    #         )

    #         # -----------------------------------------
    #         # Company filter
    #         # -----------------------------------------

    #         if company_id:

    #             # Don't allow SA to access
    #             # another company

    #             if str(company_id) != str(
    #                 logged_in_user.company_id
    #             ):
    #                 return User.objects.none()

    #             queryset = queryset.filter(
    #                 company_id=company_id
    #             )

    #         # -----------------------------------------
    #         # Plant filter
    #         # -----------------------------------------

    #         if plant_id:
    #             queryset = queryset.filter(
    #                 plant_id=plant_id
    #             )

    #         # -----------------------------------------
    #         # Department filter
    #         # -----------------------------------------

    #         if department_id:
    #             queryset = queryset.filter(
    #                 department_id=department_id
    #             )

    #         return queryset.order_by(
    #             "first_name",
    #             "last_name",
    #         )

    #     # =====================================================
    #     # HR
    #     # =====================================================

    #     if UserService.is_hr(logged_in_user):

    #         # HR must have company
    #         if not logged_in_user.company_id:
    #             return User.objects.none()

    #         # HR must have plant
    #         if not logged_in_user.plant_id:
    #             return User.objects.none()

    #         # -----------------------------------------
    #         # HR can ONLY see own company + own plant
    #         # -----------------------------------------

    #         queryset = queryset.filter(
    #             company_id=logged_in_user.company_id,
    #             plant_id=logged_in_user.plant_id,
    #         )

    #         # -----------------------------------------
    #         # Company filter
    #         # -----------------------------------------

    #         if company_id:

    #             if str(company_id) != str(
    #                 logged_in_user.company_id
    #             ):
    #                 return User.objects.none()

    #             queryset = queryset.filter(
    #                 company_id=company_id
    #             )

    #         # -----------------------------------------
    #         # Plant filter
    #         # -----------------------------------------

    #         if plant_id:

    #             if str(plant_id) != str(
    #                 logged_in_user.plant_id
    #             ):
    #                 return User.objects.none()

    #             queryset = queryset.filter(
    #                 plant_id=plant_id
    #             )

    #         # -----------------------------------------
    #         # Department filter
    #         # -----------------------------------------

    #         if department_id:
    #             queryset = queryset.filter(
    #                 department_id=department_id
    #             )

    #         return queryset.order_by(
    #             "first_name",
    #             "last_name",
    #         )

    #     # =====================================================
    #     # OTHER USERS
    #     # =====================================================

    #     return User.objects.none()

    # # =========================================================
    # # GET USER BY ID
    # # =========================================================

    # @staticmethod
    # def get_user_by_id(
    #     logged_in_user,
    #     user_id,
    # ):

    #     try:

    #         user = (
    #             User.objects
    #             .select_related(
    #                 "employee",
    #                 "company",
    #                 "plant",
    #                 "department",
    #             )
    #             .prefetch_related(
    #                 "assigned_roles__role"
    #             )
    #             .get(
    #                 id=user_id
    #             )
    #         )

    #     except User.DoesNotExist:

    #         return None

    #     # =====================================================
    #     # SUPER ADMIN
    #     # =====================================================

    #     if UserService.is_super_admin(logged_in_user):

    #         if not logged_in_user.company_id:
    #             return None

    #         if user.company_id != logged_in_user.company_id:
    #             return None

    #         return user

    #     # =====================================================
    #     # HR
    #     # =====================================================

    #     if UserService.is_hr(logged_in_user):

    #         if not logged_in_user.company_id:
    #             return None

    #         if not logged_in_user.plant_id:
    #             return None

    #         # Same company
    #         if user.company_id != logged_in_user.company_id:
    #             return None

    #         # Same plant
    #         if user.plant_id != logged_in_user.plant_id:
    #             return None

    #         return user

    #     # =====================================================
    #     # OTHER USERS
    #     # =====================================================

    #     return None

    @staticmethod
    def get_users(
        logged_in_user,
        company_id=None,
        plant_id=None,
        department_id=None,
        employee_code=None,
        email=None,
        first_name=None,
        last_name=None,
        search=None,
        is_active=None,
        is_staff=None,
        is_superuser=None,
        role_id=None,
    ):

        # -----------------------------------------------------
        # BASE QUERY
        # -----------------------------------------------------

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

        # if UserService.is_super_admin(logged_in_user):

        #     # -------------------------------------------------
        #     # If Super Admin has company assigned
        #     # restrict to that company.
        #     #
        #     # If Super Admin has NO company:
        #     # allow company filter to determine the company.
        #     # -------------------------------------------------

        #     if logged_in_user.company_id:

        #         queryset = queryset.filter(
        #             company_id=logged_in_user.company_id
        #         )

        #         # Requested company must match logged-in SA
        #         if company_id:

        #             if str(company_id) != str(
        #                 logged_in_user.company_id
        #             ):
        #                 return User.objects.none()

        #             queryset = queryset.filter(
        #                 company_id=company_id
        #             )

        #     else:

        #         # Global Super Admin
        #         if company_id:
        #             queryset = queryset.filter(
        #                 company_id=company_id
        #             )

        # # =====================================================
        # # HR / PLANT HR
        # # =====================================================

        # elif UserService.is_hr(logged_in_user):

        #     # -------------------------------------------------
        #     # HR must have company
        #     # -------------------------------------------------

        #     if not logged_in_user.company_id:
        #         return User.objects.none()

        #     # -------------------------------------------------
        #     # HR must have plant
        #     # -------------------------------------------------

        #     if not logged_in_user.plant_id:
        #         return User.objects.none()

        #     # -------------------------------------------------
        #     # HR can only see own company + own plant
        #     # -------------------------------------------------

        #     queryset = queryset.filter(
        #         company_id=logged_in_user.company_id,
        #         plant_id=logged_in_user.plant_id,
        #     )

        #     # -------------------------------------------------
        #     # Company validation
        #     # -------------------------------------------------

        #     if company_id:

        #         if str(company_id) != str(
        #             logged_in_user.company_id
        #         ):
        #             return User.objects.none()

        #     # -------------------------------------------------
        #     # Plant validation
        #     # -------------------------------------------------

        #     if plant_id:

        #         if str(plant_id) != str(
        #             logged_in_user.plant_id
        #         ):
        #             return User.objects.none()

        # # =====================================================
        # # OTHER USERS
        # # =====================================================

        # else:
        #     return User.objects.none()

        # =====================================================
        # ORGANIZATION FILTERS
        # =====================================================

        # -----------------------------------------------------
        # Company
        # -----------------------------------------------------

        if company_id:
            queryset = queryset.filter(
                company_id=company_id
            )

        # -----------------------------------------------------
        # Plant
        # -----------------------------------------------------

        if plant_id:
            queryset = queryset.filter(
                plant_id=plant_id
            )

        # -----------------------------------------------------
        # Department
        # -----------------------------------------------------

        if department_id:
            queryset = queryset.filter(
                department_id=department_id
            )

        # =====================================================
        # EMPLOYEE FILTERS
        # =====================================================

        # -----------------------------------------------------
        # Employee Code
        # -----------------------------------------------------

        if employee_code:
            queryset = queryset.filter(
                employee__employee_code__icontains=employee_code
            )

        # -----------------------------------------------------
        # Email
        # -----------------------------------------------------

        if email:
            queryset = queryset.filter(
                email__icontains=email
            )

        # -----------------------------------------------------
        # First Name
        # -----------------------------------------------------

        if first_name:
            queryset = queryset.filter(
                first_name__icontains=first_name
            )

        # -----------------------------------------------------
        # Last Name
        # -----------------------------------------------------

        if last_name:
            queryset = queryset.filter(
                last_name__icontains=last_name
            )

        # =====================================================
        # SEARCH
        # =====================================================

        if search:

            queryset = queryset.filter(
                Q(first_name__icontains=search)
                |
                Q(last_name__icontains=search)
                |
                Q(email__icontains=search)
                |
                Q(employee__employee_code__icontains=search)
            )

        # =====================================================
        # STATUS FILTERS
        # =====================================================

        if is_active is not None:

            queryset = queryset.filter(
                is_active=is_active
            )

        if is_staff is not None:

            queryset = queryset.filter(
                is_staff=is_staff
            )

        if is_superuser is not None:

            queryset = queryset.filter(
                is_superuser=is_superuser
            )

        # =====================================================
        # ROLE FILTER
        # =====================================================

        if role_id:

            queryset = queryset.filter(
                assigned_roles__role_id=role_id
            )

        # =====================================================
        # REMOVE DUPLICATES
        # =====================================================

        queryset = queryset.distinct()

        # =====================================================
        # ORDER
        # =====================================================

        return queryset.order_by(
            "first_name",
            "last_name",
            "email",
        )

    @staticmethod
    def get_user_by_id(logged_in_user, user_id):

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
                .get(id=user_id)
            )

        except User.DoesNotExist:
            return None

        # ---------------------------------------------------------
        # SUPER ADMIN
        # ---------------------------------------------------------

        if UserService.is_super_admin(logged_in_user):

            # Global Super Admin
            if not logged_in_user.company_id:
                return user

            # Company-level Super Admin
            if user.company_id != logged_in_user.company_id:
                return None

            return user

        # ---------------------------------------------------------
        # HR
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # OTHER USERS
        # ---------------------------------------------------------

        return None
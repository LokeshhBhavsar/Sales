# from django.contrib.auth import get_user_model
# from django.db.models import Prefetch
# from django.utils import timezone
# from rest_framework.exceptions import AuthenticationFailed

# from apps.accounts.models.user_role import UserRole
# from apps.accounts.models.user_permission import UserPermission

# from apps.accounts.services.jwt_service import JWTService
# from apps.accounts.services.session_service import SessionService
# from apps.accounts.services.audit_service import AuditService


# User = get_user_model()


# class AuthService:

#     @staticmethod
#     def login(email,password,request):
#         """
#         Authenticate User and Create Login Session
#         """
#         try:
#             user = (
#             User.objects.select_related(
#                 "company",
#                 "plant",
#                 "department"
#             ).prefetch_related(
#                 Prefetch(
#                     "userrole_set",
#                     queryset=UserRole.objects.select_related("role")
#                 ),
#                 Prefetch(
#                     "userpermission_set",
#                     queryset=UserPermission.objects.select_related("permission")
#                 )
#             )
#             .get(email=email)
#             )
#         except User.DoesNotExist:

#             AuditService.failed_login(
#                 email=email,
#                 request=request
#             )

#             raise AuthenticationFailed(
#                 "USER DOES NOZT EXIST."
#             )
#         #.....................................................
#         # verify password
#         #.....................................................
#         if not user.check_password(password):
#             AuditService.failed_login(
#                 email=email,
#                 request=request

#             )
#             raise AuthenticationFailed(
#                 "Invalid Password"
#             )

#         #check active user
#         if not user.is_active:
#             raise AuthenticationFailed(
#                 "Your account has been Deactivate"
#             )
#  # ---------------------------------------------------------
#         # Update Last Login
#         # ---------------------------------------------------------

#         user.last_login = timezone.now()

#         user.save(
#             update_fields=[
#                 "last_login"
#             ]
#         )
#                 # ---------------------------------------------------------
#         # Load Roles
#         # ---------------------------------------------------------

#         roles = [

#             {
#                 "id": str(item.role.id),
#                 "name": item.role.name,
#                 "code": item.role.code
#             }

#             for item in user.userrole_set.all()

#         ]

#     # ---------------------------------------------------------
#         # Load Role Permissions
#         # ---------------------------------------------------------

#         role_permissions = set()

#         for user_role in user.userrole_set.all():

#             permissions = role_permissions.objects.filter(
#                 role=user_role.role
#             ).select_related(
#                 "permission"
#             )

#             for permission in permissions:

#                 role_permissions.add(
#                     permission.permission.code
#                 )

#         # ---------------------------------------------------------
#         # Load Direct User Permissions
#         # ---------------------------------------------------------

#         direct_permissions = {

#             item.permission.code

#             for item in user.userpermission_set.all()

#         }

#         # ---------------------------------------------------------
#         # Merge Role + Direct Permissions
#         # Remove Duplicate Permissions
#         # ---------------------------------------------------------

#         permissions = sorted(

#             role_permissions.union(
#                 direct_permissions
#             )

#         )

#         #generate token
#         access_token = JWTService.generate_access_token(
#             user
#         )
#         refresh_token = JWTService.generate_refresh_token(
#             user
#         )

#         #.......................................................
#         # Create Session
#         #.......................................................
#         SessionService.create_user_session(
#             user=user,
#             refresh_token=refresh_token,
#             request=request
#         )
#         # -----------------------------------
#         # Audit Log
#         # -----------------------------------
#         AuditService.login(
#             user=user,
#             request=request
#         )

#        # -----------------------------------
#        # Roles
#        # -----------------------------------
#         roles =[
#            {
#              "id" : str(item.role.id),
#              "name": item.role.name,
#              "code": item.role.code
#            }
#            for item in user.userrole_set.all()
#        ]
  
#         # -----------------------------------
#         # Response
#         # -----------------------------------
#         return {
#         "success":True,
#         "message":"Login Successful",
#         "data":{
#           "user":{
#               "id": str(user.id),
#               "email": user.email,
#               "first_name":user.first_name,
#               "last_name":user.last_name,
#               "full_name": user.full_name,
#               "company":{
#                   "id":str(user.company.id),
#                   "name":user.company.name
#               }
#               if user.company else None,
#               "plant":{
#                   "id":str(user.plant.id),
#                   "name":user.plant.name
#               } if user.plant else None,
#               "department": {
#                   "id":str(user.department.id),
#                   "name":user.department.name
#               } if user.department else None,
#           },
#           "roles": roles,
#           "permissions":permissions,
#           "access_token": access_token,
#           "refresh_token": refresh_token
#         }
#     }



from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.utils import timezone

from rest_framework.exceptions import AuthenticationFailed

from apps.accounts.models.user_role import UserRole
from apps.accounts.models.user_permission import UserPermission
from apps.accounts.models.role_permission import RolePermission

from apps.accounts.models.user_session import UserSession
from apps.accounts.services.jwt_service import JWTService
from apps.accounts.services.session_service import SessionService
from apps.accounts.services.audit_service  import AuditService  


User = get_user_model()


class AuthService:

    @staticmethod
    def login(email, password, request):
        """
        Authenticate user and create login session.
        """

        # -------------------------------------------------
        # Get User
        # -------------------------------------------------

        try:

            user = (
                User.objects
                .select_related(
                    "company",
                    "plant",
                    "department"
                )
                .prefetch_related(

                    Prefetch(
                        "userrole_set",
                        queryset=UserRole.objects.select_related("role")
                    ),

                    Prefetch(
                        "userpermission_set",
                        queryset=UserPermission.objects.select_related("permission")
                    )

                )
                .get(email=email)
            )

        except User.DoesNotExist:

            AuditService.failed_login(
                email=email,
                request=request
            )

            raise AuthenticationFailed(
                "Invalid email or password."
            )

        # -------------------------------------------------
        # Verify Password
        # -------------------------------------------------

        if not user.check_password(password):

            AuditService.failed_login(
                email=email,
                request=request
            )

            raise AuthenticationFailed(
                "Invalid email or password."
            )

        # -------------------------------------------------
        # Check User Active
        # -------------------------------------------------

        if not user.is_active:

            raise AuthenticationFailed(
                "Your account has been deactivated."
            )

        # -------------------------------------------------
        # Update Last Login
        # -------------------------------------------------

        user.last_login = timezone.now()

        user.save(
            update_fields=[
                "last_login"
            ]
        )

        # -------------------------------------------------
        # User Roles
        # -------------------------------------------------

        roles = [

            {
                "id": str(item.role.id),
                "name": item.role.name,
                "code": item.role.code
            }

            for item in user.userrole_set.all()

        ]

        # -------------------------------------------------
        # Role Permissions
        # -------------------------------------------------

        role_permissions = set()

        for user_role in user.userrole_set.all():

            permissions = (
                RolePermission.objects
                .filter(role=user_role.role)
                .select_related("permission")
            )

            for permission in permissions:

                role_permissions.add(
                    permission.permission.code
                )

        # -------------------------------------------------
        # Direct User Permissions
        # -------------------------------------------------

        direct_permissions = {

            item.permission.code

            for item in user.userpermission_set.all()

        }

        # -------------------------------------------------
        # Merge Permissions
        # -------------------------------------------------

        permissions = sorted(
            role_permissions.union(
                direct_permissions
            )
        )

        # -------------------------------------------------
        # Generate JWT Tokens
        # -------------------------------------------------

        access_token = JWTService.generate_access_token(
            user
        )

        refresh_token = JWTService.generate_refresh_token(
            user
        )

        # -------------------------------------------------
        # Create User Session
        # -------------------------------------------------

        SessionService.create_user_session(
            user=user,
            refresh_token=refresh_token,
            request=request
        )

        # -------------------------------------------------
        # Audit Log
        # -------------------------------------------------

        AuditService.login(
            user=user,
            request=request
        )

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        return {

            "success": True,

            "message": "Login Successful",

            "data": {

                "user": {

                    "id": str(user.id),

                    "email": user.email,

                    "first_name": user.first_name,

                    "last_name": user.last_name,

                    "full_name": user.full_name,

                    "company": {

                        "id": str(user.company.id),

                        "name": user.company.name

                    } if user.company else None,

                    "plant": {

                        "id": str(user.plant.id),

                        "name": user.plant.name

                    } if user.plant else None,

                    "department": {

                        "id": str(user.department.id),

                        "name": user.department.name

                    } if user.department else None,

                },

                "roles": roles,

                "permissions": permissions,

                "access_token": access_token,

                "refresh_token": refresh_token

            }

        }



    @staticmethod
    def refresh_token(
        refresh_token,
        request
    ):
        """
        Validate refresh token and generate new tokens.
        """

        # ---------------------------------------------------------
        # Decode Refresh Token
        # ---------------------------------------------------------

        payload = JWTService.verify_refresh_token(
            refresh_token
        )

        user_id = payload.get("user_id")

        if not user_id:
            raise AuthenticationFailed(
                "Invalid refresh token."
            )

        # ---------------------------------------------------------
        # Get Active Session
        # ---------------------------------------------------------

        session = UserSession.objects.select_related(
            "user"
        ).filter(
            user_id=user_id,
            is_active=True
        ).first()

        if not session:
            raise AuthenticationFailed(
                "Session not found."
            )

        # ---------------------------------------------------------
        # Verify Refresh Token Hash
        # ---------------------------------------------------------

        token_hash = SessionService.hash_refresh_token(
            refresh_token
        )

        if session.refresh_token_hash != token_hash:
            raise AuthenticationFailed(
                "Invalid refresh token."
            )

        # ---------------------------------------------------------
        # Check User Status
        # ---------------------------------------------------------

        user = session.user

        if not user.is_active:
            raise AuthenticationFailed(
                "Your account has been deactivated."
            )

        # ---------------------------------------------------------
        # Generate New Tokens
        # ---------------------------------------------------------

        new_access_token = JWTService.generate_access_token(
            user
        )

        new_refresh_token = JWTService.generate_refresh_token(
            user
        )

        # ---------------------------------------------------------
        # Update Session
        # ---------------------------------------------------------

        session.refresh_token_hash = SessionService.hash_refresh_token(
            new_refresh_token
        )

        session.save(
            update_fields=[
                "refresh_token_hash"
            ]
        )

        # ---------------------------------------------------------
        # Response
        # ---------------------------------------------------------

        return {

            "success": True,

            "message": "Access token refreshed successfully.",

            "data": {

                "access_token": new_access_token,

                "refresh_token": new_refresh_token

            }

        }   

    def logout(
        user,
        refresh_token,
        request
    ):
        """
        Logout user and deactivate the current session.
        """

        token_hash = SessionService.hash_refresh_token(
            refresh_token
        )

        session = UserSession.objects.filter(
            user=user,
            refresh_token_hash=token_hash,
            is_active=True
        ).first()

        if not session:
            raise AuthenticationFailed(
                "Session not found."
            )

        # -----------------------------------------
        # Deactivate Session
        # -----------------------------------------

        session.is_active = False
        session.logged_out_at = timezone.now()
        session.last_activity = timezone.now()

        session.save(
            update_fields=[
                "is_active",
                "logged_out_at",
                "last_activity",
            ]
        )

        # -----------------------------------------
        # Audit Log
        # -----------------------------------------

        AuditService.logout(
            user=user,
            request=request
        )

        return {
            "success": True,
            "message": "Logout successful."
        }
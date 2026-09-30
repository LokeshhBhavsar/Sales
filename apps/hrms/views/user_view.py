# # from rest_framework.views import APIView
# # from rest_framework.permissions import IsAuthenticated
# # from rest_framework.response import Response
# # from rest_framework import status

# # from apps.accounts.permissions import (
# #     IsPlantHROrSuperAdmin,
# # )

# # from apps.hrms.serializers.user_serializer import (
# #     CreateUserSerializer,
# #     UserSerializer,
# # )

# # from apps.hrms.services.user_service import (
# #     UserService,
# # )


# # class UserCreateView(APIView):

# #     permission_classes = [
# #         IsAuthenticated,
# #         IsPlantHROrSuperAdmin,
# #     ]

# #     def post(self, request):

# #         serializer = CreateUserSerializer(
# #             data=request.data,
# #             context={
# #                 "request": request,
# #             }
# #         )

# #         serializer.is_valid(
# #             raise_exception=True
# #         )

# #         user = UserService.create_user(
# #             serializer.validated_data
# #         )

# #         return Response(
# #             {
# #                 "success": True,
# #                 "message":
# #                     "User created successfully.",
# #                 "data":
# #                     UserSerializer(user).data,
# #             },
# #             status=status.HTTP_201_CREATED,
# #         )


# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status

# # from apps.accounts.permissions import (
# #     # IsPlantHROrSuperAdmin,
# #     IsSuperAdmin,
# # )

# from apps.hrms.serializers.user_serializer import (
#     CreateUserSerializer,
#     UserListSerializer,
#     UserSerializer,
# )

# from apps.hrms.services.user_service import (
#     UserService,
# )


# # =========================================================
# # CREATE USER
# # =========================================================

# class UserCreateView(APIView):

#     permission_classes = [
#         IsAuthenticated,
#         # IsPlantHROrSuperAdmin,
#         # IsSuperAdmin,
#     ]

#     def post(self, request):

#         serializer = CreateUserSerializer(
#             data=request.data,
#             context={
#                 "request": request,
#             }
#         )

#         serializer.is_valid(
#             raise_exception=True
#         )

#         user = UserService.create_user(
#             serializer.validated_data
#         )

#         return Response(
#             {
#                 "success": True,
#                 "message":
#                     "User created successfully.",
#                 "data":
#                     UserSerializer(user).data,
#             },
#             status=status.HTTP_201_CREATED,
#         )


# # =========================================================
# # FETCH USERS
# # =========================================================
# # class UserListView(APIView):

# #     permission_classes = [
# #         IsAuthenticated,
# #         IsPlantHROrSuperAdmin,
# #     ]

# #     def get(self, request):

# #         company_id = request.query_params.get("company")
# #         plant_id = request.query_params.get("plant")
# #         department_id = request.query_params.get("department")

# #         users = UserService.get_users(
# #             logged_in_user=request.user,
# #             company_id=company_id,
# #             plant_id=plant_id,
# #             department_id=department_id,
# #         )

# #         serializer = UserListSerializer(
# #             users,
# #             many=True
# #         )

# #         return Response(
# #             {
# #                 "success": True,
# #                 "count": users.count(),
# #                 "data": serializer.data,
# #             },
# #             status=status.HTTP_200_OK,
# #         )


# class UserListView(APIView):

#     permission_classes = [
#         IsAuthenticated,
#         # IsPlantHROrSuperAdmin,
#         # IsSuperAdmin,
#     ]

#     # =====================================================
#     # GET USERS
#     # =====================================================

#     def get(self, request):

#         # =================================================
#         # ORGANIZATION FILTERS
#         # =================================================

#         company_id = request.query_params.get(
#             "company"
#         )

#         plant_id = request.query_params.get(
#             "plant"
#         )

#         department_id = request.query_params.get(
#             "department"
#         )

#         # =================================================
#         # USER FILTERS
#         # =================================================

#         employee_code = request.query_params.get(
#             "employee_code"
#         )

#         email = request.query_params.get(
#             "email"
#         )

#         first_name = request.query_params.get(
#             "first_name"
#         )

#         last_name = request.query_params.get(
#             "last_name"
#         )

#         search = request.query_params.get(
#             "search"
#         )

#         # =================================================
#         # BOOLEAN FILTERS
#         # =================================================

#         is_active = self.get_boolean_param(
#             request,
#             "is_active"
#         )

#         is_staff = self.get_boolean_param(
#             request,
#             "is_staff"
#         )

#         is_superuser = self.get_boolean_param(
#             request,
#             "is_superuser"
#         )

#         # =================================================
#         # ROLE
#         # =================================================

#         role_id = request.query_params.get(
#             "role"
#         )

#         # =================================================
#         # FETCH USERS
#         # =================================================

#         users = UserService.get_users(

#             logged_in_user=request.user,

#             company_id=company_id,

#             plant_id=plant_id,

#             department_id=department_id,

#             employee_code=employee_code,

#             email=email,

#             first_name=first_name,

#             last_name=last_name,

#             search=search,

#             is_active=is_active,

#             is_staff=is_staff,

#             is_superuser=is_superuser,

#             role_id=role_id,
#         )

#         # =================================================
#         # SERIALIZE
#         # =================================================

#         serializer = UserListSerializer(
#             users,
#             many=True
#         )

#         # =================================================
#         # RESPONSE
#         # =================================================

#         return Response(
#             {
#                 "success": True,
#                 "count": users.count(),
#                 "data": serializer.data,
#             },
#             status=status.HTTP_200_OK,
#         )

#     # =====================================================
#     # BOOLEAN PARAMETER
#     # =====================================================

#     @staticmethod
#     def get_boolean_param(
#         request,
#         parameter_name
#     ):

#         value = request.query_params.get(
#             parameter_name
#         )

#         if value is None:
#             return None

#         value = value.strip().lower()

#         if value in [
#             "true",
#             "1",
#             "yes",
#         ]:
#             return True

#         if value in [
#             "false",
#             "0",
#             "no",
#         ]:
#             return False

#         return None

# # =========================================================
# # FETCH USER BY ID
# # =========================================================

# # class UserDetailView(APIView):

# #     permission_classes = [
# #         IsAuthenticated,
# #         IsPlantHROrSuperAdmin,
# #     ]

# #     def get(self, request, user_id):

# #         user = UserService.get_user_by_id(
# #             logged_in_user=request.user,
# #             user_id=user_id,
# #         )

# #         if not user:

# #             return Response(
# #                 {
# #                     "success": False,
# #                     "message":
# #                         "User not found or you do not "
# #                         "have permission to access this user.",
# #                 },
# #                 status=status.HTTP_404_NOT_FOUND,
# #             )

# #         serializer = UserSerializer(user)

# #         return Response(
# #             {
# #                 "success": True,
# #                 "data": serializer.data,
# #             },
# #             status=status.HTTP_200_OK,
# #         )


# class UserDetailView(APIView):

#     permission_classes = [
#         IsAuthenticated,
#         # IsPlantHROrSuperAdmin,
#         # IsSuperAdmin,
#     ]

#     def get(self, request, user_id):

#         user = UserService.get_user_by_id(
#             logged_in_user=request.user,
#             user_id=user_id,
#         )

#         if not user:
#             return Response(
#                 {
#                     "success": False,
#                     "message": (
#                         "User not found or you do not "
#                         "have permission to access this user."
#                     ),
#                 },
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         serializer = UserSerializer(user)

#         return Response(
#             {
#                 "success": True,
#                 "data": serializer.data,
#             },
#             status=status.HTTP_200_OK,
#         )

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.hrms.serializers.user_serializer import (
    CreateUserSerializer,
    UserListSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

from apps.hrms.services.user_service import (
    UserService,
)


# =========================================================
# CREATE USER
# =========================================================

class UserCreateView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):

        serializer = CreateUserSerializer(
            data=request.data,
            context={
                "request": request,
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = UserService.create_user(
            serializer.validated_data
        )

        return Response(
            {
                "success": True,
                "message": "User created successfully.",
                "data": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# FETCH USERS
# =========================================================

class UserListView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):

        # =================================================
        # ORGANIZATION FILTERS
        # =================================================

        company_id = request.query_params.get(
            "company"
        )

        plant_id = request.query_params.get(
            "plant"
        )

        department_id = request.query_params.get(
            "department"
        )

        # =================================================
        # USER FILTERS
        # =================================================

        employee_code = request.query_params.get(
            "employee_code"
        )

        email = request.query_params.get(
            "email"
        )

        first_name = request.query_params.get(
            "first_name"
        )

        last_name = request.query_params.get(
            "last_name"
        )

        search = request.query_params.get(
            "search"
        )

        # =================================================
        # BOOLEAN FILTERS
        # =================================================

        is_active = self.get_boolean_param(
            request,
            "is_active"
        )

        is_staff = self.get_boolean_param(
            request,
            "is_staff"
        )

        is_superuser = self.get_boolean_param(
            request,
            "is_superuser"
        )

        # =================================================
        # ROLE
        # =================================================

        role_id = request.query_params.get(
            "role"
        )

        # =================================================
        # FETCH USERS
        # =================================================

        users = UserService.get_users(
            logged_in_user=request.user,
            company_id=company_id,
            plant_id=plant_id,
            department_id=department_id,
            employee_code=employee_code,
            email=email,
            first_name=first_name,
            last_name=last_name,
            search=search,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser,
            role_id=role_id,
        )

        # =================================================
        # SERIALIZE
        # =================================================

        serializer = UserListSerializer(
            users,
            many=True
        )

        # =================================================
        # RESPONSE
        # =================================================

        return Response(
            {
                "success": True,
                "count": users.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # BOOLEAN PARAMETER
    # =====================================================

    @staticmethod
    def get_boolean_param(
        request,
        parameter_name
    ):

        value = request.query_params.get(
            parameter_name
        )

        if value is None:
            return None

        value = value.strip().lower()

        if value in [
            "true",
            "1",
            "yes",
        ]:
            return True

        if value in [
            "false",
            "0",
            "no",
        ]:
            return False

        return None


# =========================================================
# FETCH USER BY ID
# =========================================================

class UserDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, user_id):

        user = UserService.get_user_by_id(
            logged_in_user=request.user,
            user_id=user_id,
        )

        if not user:

            return Response(
                {
                    "success": False,
                    "message": (
                        "User not found or you do not "
                        "have permission to access this user."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserSerializer(user)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
        # =====================================================
    # UPDATE USER
    # =====================================================

    def put(self, request, user_id):

        user = UserService.get_user_by_id(
            logged_in_user=request.user,
            user_id=user_id,
        )

        if not user:

            return Response(
                {
                    "success": False,
                    "message": (
                        "User not found or you do not "
                        "have permission to update this user."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserUpdateSerializer(
            user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = UserService.update_user(
            user,
            serializer.validated_data,
        )

        return Response(
            {
                "success": True,
                "message": "User updated successfully.",
                "data": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # DELETE USER
    # =====================================================

    def delete(self, request, user_id):

        user = UserService.get_user_by_id(
            logged_in_user=request.user,
            user_id=user_id,
        )

        if not user:

            return Response(
                {
                    "success": False,
                    "message": (
                        "User not found or you do not "
                        "have permission to delete this user."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        UserService.delete_user(
            user
        )

        return Response(
            {
                "success": True,
                "message": "User deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
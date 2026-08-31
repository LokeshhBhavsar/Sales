# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status

# from apps.accounts.permissions import (
#     IsPlantHROrSuperAdmin,
# )

# from apps.hrms.serializers.user_serializer import (
#     CreateUserSerializer,
#     UserSerializer,
# )

# from apps.hrms.services.user_service import (
#     UserService,
# )


# class UserCreateView(APIView):

#     permission_classes = [
#         IsAuthenticated,
#         IsPlantHROrSuperAdmin,
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


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.accounts.permissions import (
    IsPlantHROrSuperAdmin,
)

from apps.hrms.serializers.user_serializer import (
    CreateUserSerializer,
    UserListSerializer,
    UserSerializer,
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
        IsPlantHROrSuperAdmin,
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
                "message":
                    "User created successfully.",
                "data":
                    UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# FETCH USERS
# =========================================================
class UserListView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsPlantHROrSuperAdmin,
    ]

    def get(self, request):

        company_id = request.query_params.get("company")
        plant_id = request.query_params.get("plant")
        department_id = request.query_params.get("department")

        users = UserService.get_users(
            logged_in_user=request.user,
            company_id=company_id,
            plant_id=plant_id,
            department_id=department_id,
        )

        serializer = UserListSerializer(
            users,
            many=True
        )

        return Response(
            {
                "success": True,
                "count": users.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# FETCH USER BY ID
# =========================================================

class UserDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsPlantHROrSuperAdmin,
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
                    "message":
                        "User not found or you do not "
                        "have permission to access this user.",
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
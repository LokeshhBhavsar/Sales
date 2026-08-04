from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.authentication import JWTAuthentication
from apps.accounts.models.role import Role
from apps.accounts.serializers.role_serializer import (
    RoleCreateSerializer,
    RoleUpdateSerializer,
    RoleListSerializer,
)
from apps.accounts.services.role_service import RoleService


class RoleCreateView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        if not request.user.is_superuser:
            return Response(
                {
                    "message": "Only Super Admin can create roles."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RoleCreateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        role = RoleService.create_role(
            serializer.validated_data
        )

        return Response(
            {
                "message": "Role created successfully.",
                "data": RoleListSerializer(role).data,
            },
            status=status.HTTP_201_CREATED,
        )


class RoleListView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        roles = RoleService.get_roles()

        serializer = RoleListSerializer(
            roles,
            many=True
        )

        return Response(
            {
                "message": "Roles fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class RoleDetailView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, role_id):

        try:
            role = RoleService.get_role(
                role_id
            )

        except Role.DoesNotExist:
            return Response(
                {
                    "message": "Role not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RoleListSerializer(
            role
        )

        return Response(
            {
                "message": "Role fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, role_id):

        if not request.user.is_superuser:
            return Response(
                {
                    "message": "Only Super Admin can update roles."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            role = RoleService.get_role(
                role_id
            )

        except Role.DoesNotExist:
            return Response(
                {
                    "message": "Role not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RoleUpdateSerializer(
            role,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        role = RoleService.update_role(
            role,
            serializer.validated_data,
        )

        return Response(
            {
                "message": "Role updated successfully.",
                "data": RoleListSerializer(role).data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, role_id):

        if not request.user.is_superuser:
            return Response(
                {
                    "message": "Only Super Admin can delete roles."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            role = RoleService.get_role(
                role_id
            )

        except Role.DoesNotExist:
            return Response(
                {
                    "message": "Role not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        RoleService.delete_role(
            role
        )

        return Response(
            {
                "message": "Role deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT,
        )
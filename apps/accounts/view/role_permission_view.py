from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsSuperAdmin

from apps.accounts.models.role_permission import RolePermission

from apps.accounts.serializers.role_permission_serializer import (
    RolePermissionAssignSerializer,
    RolePermissionSerializer,
)

from apps.accounts.services.role_permission_service import (
    RolePermissionService,
)
class RolePermissionView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsSuperAdmin,
    ]

    def post(self, request):

        serializer = RolePermissionAssignSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        role_permission = RolePermissionService.assign_permission(
            serializer.validated_data
        )

        return Response({
            "success": True,
            "message": "Permission assigned successfully.",
            "data": RolePermissionSerializer(
                role_permission
            ).data
        })

    def get(self, request):

        role_id = request.query_params.get("role_id")

        queryset = RolePermission.objects.select_related(
            "role",
            "permission",
            "permission__company",
            "permission__plant",
            "permission__department"
        )

        if role_id:
            queryset = queryset.filter(
                role_id=role_id
            )

        serializer = RolePermissionSerializer(
            queryset,
            many=True
        )

        return Response({
            "success": True,
            "count": queryset.count(),
            "data": serializer.data
        })
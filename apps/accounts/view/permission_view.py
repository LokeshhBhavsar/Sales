from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsSuperAdmin

from apps.accounts.models.permission import Permission

from apps.accounts.serializers.permission_serializer import (
    PermissionCreateSerializer,
    
)

from apps.accounts.services.permission_service import (
    PermissionService,
)


class PermissionView(APIView):
    """
    Permission APIs

    POST -> Create Permission
    GET  -> List Permissions
    """

    permission_classes = [
        IsAuthenticated,
        IsSuperAdmin,
    ]

    def post(self, request):
        """
        Create Permission
        """

        serializer = PermissionCreateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        permission = PermissionService.create_permission(
            serializer.validated_data
        )

        return Response(
            {
                "success": True,
                "message": "Permission created successfully.",
                "data": PermissionCreateSerializer(
                    permission
                ).data
            },
            status=status.HTTP_201_CREATED
        )

    def get(self, request):
        """
        List All Permissions
        """

        permissions = Permission.objects.all().order_by(
            "module",
            "action"
        )

        serializer = PermissionCreateSerializer(
            permissions,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Permission list fetched successfully.",
                "count": permissions.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )
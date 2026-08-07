from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.accounts.permissions import IsSuperAdmin

from apps.accounts.serializers.permission_serializer import (
    PermissionCreateSerializer,
    PermissionSerializer,
)

from apps.accounts.services.permission_service import PermissionService

from apps.accounts.models.permission import Permission


class PermissionView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsSuperAdmin,
    ]

    def post(self, request):

        serializer = PermissionCreateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        permission = PermissionService.create_permission(
            serializer.validated_data
        )

        return Response({

            "success": True,

            "message": "Permission created successfully.",

            "data": PermissionSerializer(
                permission
            ).data

        }, status=status.HTTP_201_CREATED)

    def get(self, request):

        permissions = Permission.objects.select_related(
            "company",
            "plant",
            "department"
        ).order_by(
            "module",
            "action"
        )

        serializer = PermissionSerializer(
            permissions,
            many=True
        )

        return Response({

            "success": True,

            "count": permissions.count(),

            "data": serializer.data

        })


class PermissionListAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        permissions = PermissionService.get_permissions_for_user(
            request.user
        )

        serializer = PermissionSerializer(
            permissions,
            many=True
        )

        return Response({

            "success": True,

            "count": permissions.count(),

            "data": serializer.data

        })
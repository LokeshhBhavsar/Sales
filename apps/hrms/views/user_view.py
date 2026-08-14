from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.accounts.permissions import (
    IsPlantHROrSuperAdmin,
)

from apps.hrms.serializers.user_serializer import (
    CreateUserSerializer,
    UserSerializer,
)

from apps.hrms.services.user_service import (
    UserService,
)


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
from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView


from apps.accounts.serializers.refresh_token_serializer import (
    RefreshTokenSerializer,
)

from apps.accounts.services.auth_service import AuthService

class RefreshTokenView(APIView):
    """
    Refresh Access Token API
    """

    authentication_classes = []
    permission_classes = []
    def post(self,request):
        """
        generate new access token using a valid refresh token
        """

        serializer = RefreshTokenSerializer(
            data = request.data 
        )
        serializer.is_valid(
            raise_exception=True
        )

        response = AuthService.refresh_token(

        refresh_token=serializer.validated_data["refresh_token"],
     
    )
        return Response(
            response,
            status=status.HTTP_200_OK
        )
        
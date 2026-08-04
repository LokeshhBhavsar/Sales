from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


from apps.accounts.serializers.login_serializer import LoginSerializer
from apps.accounts.services.auth_service import AuthService


class LoginView(APIView):
    """
    Login Service
    """
    authentication_classes = []

    permission_classes = []

    def post(self,request):
        """
        Authenticate user and return jwt tokens
        """

        #. Validate Request Data

        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )


        # Authenticate User
        
        result = AuthService.login(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            request=request
        )

        return Response(
            result,
            status=status.HTTP_200_OK
        )
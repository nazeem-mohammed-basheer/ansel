# bodhini_project/api_views.py

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny # NEW: Import AllowAny for public access

# Custom ObtainAuthToken to return username and is_staff along with token
@method_decorator(csrf_exempt, name='dispatch') # Temporarily exempt CSRF for easier frontend testing
class CustomAuthToken(ObtainAuthToken):
    permission_classes = [AllowAny] # Explicitly allow any user (authenticated or not) to access this login endpoint

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'is_staff': user.is_staff # Return is_staff status
        })

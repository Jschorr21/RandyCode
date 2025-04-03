from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

@api_view(['POST'])
def register_user(request):
    data = request.data
    email = data.get('email', '').lower()
    password = data.get('password')

    if not email or not password:
        return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    if not email.endswith(".edu"):
        return Response({"error": "Only .edu email addresses are allowed."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=email).exists():
        return Response({"error": "User already exists."}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create(
        username=email,
        email=email,
        password=make_password(password)
    )

    return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status

@api_view(["POST"])
def register_user(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Email and password required"}, status=400)

    if not email.endswith(".edu"):
        return Response({"error": "Only .edu emails are allowed."}, status=400)

    if User.objects.filter(username=email).exists():
        return Response({"error": "User already exists."}, status=400)

    User.objects.create_user(username=email, email=email, password=password)
    return Response({"message": "User created successfully."}, status=201)

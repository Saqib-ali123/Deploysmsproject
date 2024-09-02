from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import *
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, BlacklistMixin
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.core.cache import cache


@api_view(["GET", "POST", "PUT", "DELETE"])
def UserView(request, pk=None):
    if request.method == "GET":

        if pk is not None:
            user = get_object_or_404(User, id=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)

    elif request.method == "POST":
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered in  successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        user = get_object_or_404(User, id=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User updated successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        user = get_object_or_404(User, id=pk)
        user.delete()
        return Response(
            {"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


@api_view(["POST"])
def LoginViews(request):
    if request.method == "POST":
        email = request.data.get("email")
        password = request.data.get("password")
        role = request.data.get("role")

        Serializer_Data = LoginSerializers(data=request.data)

        if Serializer_Data.is_valid():

            user = authenticate(email=email, password=password)

            if user is None:
                return Response(
                    {"Message": "Authentication failed , Invalid Email and Password"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_role = user.role.all()
            print(user_role)

            user_filter = user_role.filter(name=role).first()

            print(user_filter)

            if user_filter is None:
                return Response(
                    {"Message": "Invalid Role"}, status=status.HTTP_400_BAD_REQUEST
                )

            refresh = RefreshToken.for_user(user)
            refresh["role"] = role

            access = str(refresh.access_token)
            refresh = str(refresh)

            return Response(
                {
                    "Access Token ": access,
                    "Refresh Token ": refresh,
                    "Message": "Token Role base Authentication is Successfully",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:
            errors = Serializer_Data.errors
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)


from django.contrib.auth import logout


@api_view(["POST"])
def LogOutView(request):
    if request.method == "POST":

        serializer = LogoutSerializers(data=request.data)

        if serializer.is_valid():
            refresh_token = serializer.validated_data.get("refresh_token")

            if refresh_token:
                refresh = RefreshToken(refresh_token)
                refresh.blacklist()

                return Response(
                    {
                        "Message": "LogOut Successfuly and Refresh token convert into blacklist"
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"error": " Refresh token not provide"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"Error": "Invalid Serializer"}, status=status.HTTP_400_BAD_REQUEST
        )

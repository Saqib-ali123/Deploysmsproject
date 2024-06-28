from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import *
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated




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


@api_view(['POST'])
@permission_classes([IsAuthenticated])

def ChangePasswordView(request): #ChangePasswoordView
    current_password=request.data.get('current_password')
    Change_Password=request.data.get('change_password')
    email=request.data.get('email')

    serialized=ChangePasswordSerializer(data=request.data)

    if serialized.is_valid():
        
        user=authenticate(email=email,password=current_password)

        if user is not None:

            user.set_password(Change_Password)
            user.save()
            return Response({'Message':' Changed password Successfully'})
        
        return Response({'Message ':' Invalid Password'})
    return Response (serialized.errors, status=400)
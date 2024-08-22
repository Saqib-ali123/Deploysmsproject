from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import *
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken,BlacklistMixin
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.core.cache import cache
from django.contrib.auth import logout
from rest_framework.response import Response
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ChangePasswordView(request):
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


@api_view(['POST'])
def LoginView(request):
    if request.method== "POST":
        email=request.data.get('email')
        password=request.data.get('password')
        role=request.data.get('role')

        Serializer_Data=LoginSerializers(data=request.data)

        if Serializer_Data.is_valid():

            user =authenticate(email=email,password=password)

            if user is None:
                return Response({'Message':'Authentication failed , Invalid Email and Password'})
            
            user_role = user.role.all()
            print(user_role)

            user_filter=user_role.filter(name=role).first()

            print(user_filter)

            if user_filter is None:
                return Response({"Message":"Invalid Role"})
            

            refresh= RefreshToken.for_user(user)
            refresh['role']=role


            access=str(refresh.access_token)
            refresh=str(refresh)
            

            return Response ({"Access Token ":access, "Refresh Token ":refresh ,"Message":"Token Role base Authentication is Successfully"  })
        

        else:
            errors=Serializer_Data.errors
            return Response(errors,status=400)
        

@api_view(['POST'])  
def LogOutView(request):
    if request.method=='POST':

        serializer=LogoutSerializers(data=request.data)

        if serializer.is_valid():
            refresh_token=serializer.validated_data.get('refresh_token')

            if refresh_token:
                refresh=RefreshToken(refresh_token)
                refresh.blacklist()

                return Response({"Message":"LogOut Successfuly and Refresh token convert into blacklist"},status=status.HTTP_200_OK)
            
            return Response({"error":" Refresh token not provide"},status=status.HTTP_404_NOT_FOUND)
        
        return Response({"Error":"Invalid Serializer"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def SendOtpView(request):

    email_serialzer=OtpSerializers(data=request.data)

    if email_serialzer.is_valid():
        email=email_serialzer.validated_data['email']
        otp=get_random_string(length=6, allowed_chars='1234567890')
        cache.set(email, otp , timeout=300)

        if email is not None:
            from django.conf import settings

            send_mail(
                'Reset your Password',
                f'Your Otp for Forgot Password {otp}',
                settings.EMAIL_HOST_USER,

                [email],

                fail_silently=False
            )

            return Response({'Message':'Otp Sent to your Email'},status=status.HTTP_200_OK)
        return Response({'Message':'Invalid Email'},status=status.HTTP_204_NO_CONTENT)
    
    return Response(email_serialzer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def ForgotPasswordView(request):
    serializer_data=ForgotSerializers(data=request.data)

    if serializer_data.is_valid():
        email=serializer_data.validated_data['email']
        otp=serializer_data.validated_data['otp']
        new_password=serializer_data.validated_data['new_password']


        cached_otp=cache.get(email)

        if cached_otp==otp:
            try:
                user=User.objects.get(email=email)

            except User.DoesNotExist:

                return Response({"error":"User Not Found"},status=status.HTTP_404_NOT_FOUND)
            
            user.set_password(new_password)
            user.save()
            cache.delete(email)

            return Response({'Message':'Forgot otp Successfull'},status=status.HTTP_200_OK)
        return Response({"Message":"Invalid OTP "},status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)

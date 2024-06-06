from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import *
from rest_framework import status
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


def SendOtpView(request):

    email_serialzer=OtpSerializers(data=request.data)

    if email_serialzer.is_valid():
        email=email_serialzer.validated_data['email']
        otp=get_random_string(length=6, allowed_chars='1234567890')
        cache.set(email, otp , timeout=300)

        if email is not None:

            send_mail(
                'Forgot your Password',
                f'Your Otp for Forgot Password {otp}',
                'anasirfan502@gmail.com',

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
    
        

        
    
            
            






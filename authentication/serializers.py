from rest_framework import serializers

from authentication.models import User
from director.models import Role
from director.serializers import RoleSerializer


class UserSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), many=True, write_only=True
    )

    roles = RoleSerializer(source="role", read_only=True, many=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "password",
            "role",
            "roles",
        ]
        extra_kwargs = {"password": {"write_only": True}}


class ChangePasswordSerializer(serializers.Serializer):
    current_password=serializers.CharField(min_length=8)
    change_password = serializers.CharField(min_length=8)
    email=serializers.EmailField

# Changes as of 25April25 at 01:00 PM
class LoginSerializers(serializers.Serializer):
    email=serializers.EmailField()
    password=serializers.CharField()
    # role=serializers.CharField(max_length=30)
    

class LogoutSerializers(serializers.Serializer):
    refresh_token=serializers.CharField()


class OtpSerializers(serializers.Serializer):
    email=serializers.EmailField()


class ForgotSerializers(serializers.Serializer):
    email=serializers.EmailField()
    otp=serializers.CharField(max_length=6)
    new_password=serializers.CharField(min_length=8,write_only=True)
    confirm_password=serializers.CharField(min_length=8, write_only=True)

    def validate(self, data):
        if data ['new_password'] != data['confirm_password']:
            raise serializers.ValidationError('Passswrod dont match')
        return data


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

class LoginSerializers(serializers.Serializer):
    email=serializers.EmailField()
    password=serializers.CharField(max_length=12)
    role=serializers.CharField(max_length=30)
    



class LogoutSerializers(serializers.Serializer):
    refresh_token=serializers.CharField()
    

from rest_framework import serializers
from .models import *


class YearLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = YearLevel
        fields = "__all__"


class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolYear
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class ClassRoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoomType
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"




class BankingDetailsSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(max_length = 250, write_only = True)


    class Meta:
        model = BankingDetail
        fields = ['email', 'account_no', 'ifsc_code', 'holder_name']


    def create(self, validated_data):
        user_data = {
            'email': validated_data.pop('email')
            }
        user = User.objects.filter(email=user_data['email']).first()
        if user:

            banking_details = BankingDetail.objects.create(user=user, **validated_data)
            return banking_details
        else:
            raise serializers.ValidationError("User does not exists")
    
        
    def update(self, instance, validated_data):
        instance.user.email = validated_data.get('email', User.email)
        instance.account_no = validated_data.get('account_no', instance.account_no)
        instance.ifsc_code = validated_data.get('ifsc_code', instance.ifsc_code)
        instance.holder_name = validated_data.get('holder_name', instance.holder_name)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({
            'first_name': instance.user.first_name,
            'middle_name': instance.user.middle_name,
            'last_name': instance.user.last_name,
            'email': instance.user.email,
            'account_no': instance.account_no,
            'ifsc_code': instance.ifsc_code,
            'holder_name': instance.holder_name,
        })
        return representation


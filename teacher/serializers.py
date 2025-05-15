from rest_framework import serializers
from . models import Teacher
from authentication . models import User
from director . models import Role
from django.db import IntegrityError
from django.core.exceptions import MultipleObjectsReturned

class TeacherSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length = 250, write_only = True)
    middle_name = serializers.CharField(max_length = 250, write_only = True)
    last_name = serializers.CharField(max_length = 250, write_only = True)
    password = serializers.CharField(max_length = 250, write_only = True)
    email = serializers.EmailField(max_length = 250, write_only = True)
    
    class Meta:
        model = Teacher
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'password','email', 'phone_no', 'gender', 'adhaar_no', 'pan_no', 'qualification']


    def create(self, validated_data):
        user_data = {
            'first_name': validated_data.pop('first_name'),
            'middle_name': validated_data.pop('middle_name'),
            'last_name': validated_data.pop('last_name'),
            'password' : validated_data.pop('password'),
            'email': validated_data.pop('email')
            }
        
        try:
            role, created = Role.objects.get_or_create(name='teacher')
        except MultipleObjectsReturned:
            raise serializers.ValidationError("The role you are trying to create is already exists")

        user = User.objects.filter(email=user_data['email']).first()

        if user:
            if not user.role.filter(name = 'teacher').exists():
                user.role.add()
                user.save()

            else:
                raise serializers.ValidationError("User email already existed with the same profile")
            
        else:
            user = User.objects.create_user(**user_data)
            user.role.add(role)
            user.save()

        teacher = Teacher.objects.create(user = user, **validated_data)
        return teacher

    def update(self, instance, validated_data):
        
        instance.user.first_name = validated_data.get('first_name',instance.user.first_name)
        instance.user.middle_name = validated_data.get('middle_name', instance.user.middle_name)
        instance.user.last_name = validated_data.get('last_name',instance.user.last_name)
        instance.user.email = validated_data.get('email',   instance.user.email)
        instance.phone_no = validated_data.get('phone_no', instance.phone_no)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.adhaar_no = validated_data.get('adhaar_no', instance.adhaar_no)
        instance.pan_no = validated_data.get('pan_no', instance.pan_no)
        instance.qualification = validated_data.get('qualification', instance.qualification)
        instance.user.set_password(validated_data.get('password'))

        
        try:
            instance.user.save()
        except IntegrityError:
            raise serializers.ValidationError("User email already exists.")
        
        instance.save()
        return instance


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({
            'first_name' : instance.user.first_name,
            'middle_name' : instance.user.middle_name,
            'last_name' : instance.user.last_name,
            'email' : instance.user.email,
            'phone_no' : instance.phone_no,
            'gender' : instance.gender,
            'adhaar_no' : instance.adhaar_no,
            'pan_no' : instance.pan_no,
            'qualification' : instance.qualification
            
        })
        return representation
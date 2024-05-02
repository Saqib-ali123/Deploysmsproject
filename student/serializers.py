from rest_framework import serializers

from authentication.models import User
from director.models import Role
from .models import GuardianType, Student

from django.db import IntegrityError
from django.core.exceptions import MultipleObjectsReturned

class GuardianTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardianType
        fields = "__all__"


class StudentSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=100, write_only=True)
    middle_name = serializers.CharField(max_length=100, write_only=True)
    last_name = serializers.CharField(max_length=100, write_only=True)
    password = serializers.CharField(max_length=100, write_only=True)
    email = serializers.EmailField(write_only=True)
    classes = serializers.PrimaryKeyRelatedField(queryset='director.ClassPeriod'.objects.all(), many=True)

    

    def create(self, validated_data):
        def validate_email(self, value):
        
            # Check if the email already exists in the User table.
            
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email already exists.")
            return value
        user_data = {
            'first_name': validated_data.pop('first_name'),
            'middle_name': validated_data.pop('middle_name'),
            'last_name': validated_data.pop('last_name'),
            'password': validated_data.pop('password'),
            'email': validated_data.pop('email'),
        }
        classes_data = validated_data.pop('classes', [])

        try:
            user = User.objects.get(email=user_data['email'])
            if not user.role.filter(name='student').exists():
                role, created = Role.objects.get_or_create(name='student')
                if created:
                    user.role.add(role)
                    user.save()
        except User.DoesNotExist:
            user = User.objects.create_user(**user_data)
            role = Role.objects.create(name='student')
            user.role.add(role)
        except MultipleObjectsReturned:
            raise serializers.ValidationError("Multiple roles found for the user.")

        student = Student.objects.create(user=user, **validated_data)
        student.classes.set(classes_data)
        return student

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        email = user_data.get('email')
        
        try:
            if email:
                user_instance = User.objects.get(email=email)
                instance.user.email = email
            instance.user.first_name = validated_data.get('first_name', instance.user.first_name)
            instance.user.middle_name = validated_data.get('middle_name', instance.user.middle_name)
            instance.user.last_name = validated_data.get('last_name', instance.user.last_name)
            instance.user.password = validated_data.get('password', instance.user.password)
            instance.user.email = validated_data.get('email', instance.user.email)
            instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
            instance.gender = validated_data.get('gender', instance.gender)
            instance.enrolment_date = validated_data.get('enrolment_date', instance.enrolment_date)
            
            instance.user.save()
            instance.save()

            return instance
        except User.DoesNotExist:
            raise serializers.ValidationError("User with provided email does not exist.")
        except IntegrityError:
            raise serializers.ValidationError("User data could not be updated.Student email already exists in student table.")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({
            'first_name': instance.user.first_name,
            'middle_name': instance.user.middle_name,
            'last_name': instance.user.last_name,
            'email': instance.user.email,
            'classes': [class_period.id for class_period in instance.classes.all()],
            'date_of_birth': instance.date_of_birth,
            'gender': instance.gender,
            'enrolment_date': instance.enrolment_date,
        })
        return representation

    class Meta:
        model = Student
        fields = ['first_name', 'middle_name', 'last_name', 'password', 'email', 'classes', 'date_of_birth', 'gender', 'enrolment_date']


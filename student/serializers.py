from rest_framework import serializers

from authentication.models import User
from director.models import Role,ClassPeriod
from .models import GuardianType, Student

from django.db import IntegrityError
from django.core.exceptions import MultipleObjectsReturned

from .models import Guardian

class GuardianTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardianType
        fields = "__all__"


class StudentSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=100, write_only=True)
    middle_name = serializers.CharField(max_length=100, write_only=True, required=False)
    last_name = serializers.CharField(max_length=100, write_only=True)
    password = serializers.CharField(max_length=100, write_only=True)
    email = serializers.EmailField(write_only=True)
    classes = serializers.PrimaryKeyRelatedField(queryset=ClassPeriod.objects.all(), many=True)

    


    def create(self, validated_data):
        user_data = {
            'first_name': validated_data.pop('first_name'),
            'middle_name': validated_data.pop('middle_name', None),
            'last_name': validated_data.pop('last_name'),
            'password': validated_data.pop('password'),
            'email': validated_data.pop('email'),
        }
        classes_data = validated_data.pop('classes', [])
        
        
        try:
            role, created = Role.objects.get_or_create(name='student')
        except MultipleObjectsReturned:
            raise serializers.ValidationError("Something went wrong")
     
        user = User.objects.filter(email=user_data['email']).first()

        if  user:
            if not user.role.filter(name='student').exists():
                user.role.add(role)
                user.save()
            else:
                raise serializers.ValidationError("User with this email already exists and is a student.")
            
        else:
            user = User.objects.create_user(**user_data)
            user.role.add(role)
            user.save()

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
         
            instance.user.set_password(validated_data.get('password')) 
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
        exclude = ['user']




class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class GuardianSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True, max_length=255)
    middle_name = serializers.CharField(write_only=True, max_length=255, allow_blank=True)
    last_name = serializers.CharField(write_only=True, max_length=255)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Guardian
        exclude = ['user']

    def create(self, validated_data):
        
        user_data = {
            'first_name': validated_data.pop('first_name', ''),
            'middle_name': validated_data.pop('middle_name', ''),
            'last_name': validated_data.pop('last_name', ''),
            'email': validated_data.pop('email', ''),
            'password': validated_data.pop('password', ''),
        }

        
        guardian_data = {
            'phone_no': validated_data.pop('phone_no', '')
        }
        try:
          role_guardian,_= Role.objects.get_or_create(name='guardian')
        
        except MultipleObjectsReturned:
            raise serializers.ValidationError("somthing went wrong!")

       
        user_instance = User.objects.filter(email=user_data['email']).first()

        if user_instance:
            
            if user_instance.role.filter(name='guardian').exists():
                
                raise serializers.ValidationError({"message": "User with this email already exists as a guardian."})
            
            else:
                
         
                user_instance.role.add(role_guardian)
                guardian_profile = Guardian.objects.create(user=user_instance, **guardian_data)
                return guardian_profile
        else:
            
            user_instance = User.objects.create_user(**user_data)
            
            user_instance.role.add(role_guardian)
            guardian_profile = Guardian.objects.create(user=user_instance, **guardian_data)
            return guardian_profile

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user_data = {
            'first_name': instance.user.first_name,
            'middle_name': instance.user.middle_name,
            'last_name': instance.user.last_name,
            'email': instance.user.email,
        }
        representation.update(user_data)
        return representation
        
    
    def update(self, instance, validated_data):
        instance.phone_no = validated_data.get('phone_no', instance.phone_no)
        user_data = {
            'first_name':validated_data.get('first_name',instance.user.first_name),
            'middle_name':validated_data.get('middle_name',instance.user.middle_name),
            'last_name':validated_data.get('last_name',instance.user.last_name),
            'email':validated_data.get('email',instance.user.email),
            'password':validated_data.get('password',instance.user.password),
        }
        
        user_instance = instance.user
        user_instance.first_name = user_data['first_name']
        user_instance.middle_name = user_data['middle_name']
        user_instance.last_name =user_data['last_name']
        user_instance.email = user_data['email']
        user_instance.set_password(validated_data.get('password'))
        try:
           user_instance.save()
           instance.save()

        except User.DoesNotExist:
            raise serializers.ValidationError({"Message":"User doesn't exist with this email!"})
        
        except IntegrityError:
            raise serializers.ValidationError({"Integrity Error" :" Unable to update Data"})
        
        except Exception:
           raise serializers.ValidationError({"Message":"Somthing went wrong"})
        return instance
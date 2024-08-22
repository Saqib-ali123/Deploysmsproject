from rest_framework import serializers
from .models import *
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError

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







class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

    def create_or_get_role(self, role_name):
        existing_role = Role.objects.filter(name=role_name).first()
        if existing_role:
            return existing_role
        else:
            new_role = Role.objects.create(name=role_name)
            return new_role



# ========================Address========================
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'



class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['user', 'house_no', 'area_code', 'country', 'state', 'city', 'address_line']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['country'] = instance.country.name
        representation['state'] = instance.state.name
        representation['city'] = instance.city.name
        return representation

# ======================PeriodSerializer==================================
class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolYear
        fields = '__all__'
        # fields = ['year_name']

class PeriodSerializer(serializers.ModelSerializer):
    year = serializers.PrimaryKeyRelatedField(queryset=SchoolYear.objects.all())

    class Meta:
        model = Period
        fields = ['year', 'name', 'start_period_time', 'end_period_time']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            representation['year'] = instance.year.year_name
        except AttributeError:
            # Handle the case where 'year' is None or does not have the attribute 'year_name'
            representation['year'] = None # to indicate that the year is not available.
        return representation
    

class DirectorProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=100, write_only=True)
    middle_name = serializers.CharField(max_length=100, write_only=True, allow_blank=True, required=False)
    last_name = serializers.CharField(max_length=100, write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Director
        exclude = ['user']

    def create(self, validated_data):
        
        user_data = {
            'first_name': validated_data.pop('first_name'),
            'middle_name': validated_data.pop('middle_name', ''),
            'last_name': validated_data.pop('last_name'),
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password'),
        }
        try:
            role, created = Role.objects.get_or_create(name='director')
        
        except MultipleObjectsReturned:
            raise serializers.ValidationError("Something went wrong")
            
        user = User.objects.filter(email=user_data['email']).first()
        if user:
                
            if not user.role.filter(name='director').exists():
             user.role.add(role)
        else:
        
            user = User.objects.create_user(**user_data)
            user.role.add(role)
            user.save()

        try:
          director_profile = Director.objects.create(user=user, **validated_data)

        except IntegrityError:
           raise serializers.ValidationError("user with this email is already exists")  
        
        return director_profile

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        data = {
            'first_name': instance.user.first_name,
            'middle_name': instance.user.middle_name,
            'last_name': instance.user.last_name,
            'email': instance.user.email,
        }
        representation.update(data)
        return representation

    def update(self, instance, validated_data):
 
     user_data = {
        'first_name': validated_data.get('first_name', instance.user.first_name),
        'middle_name': validated_data.get('middle_name', instance.user.middle_name),
        'last_name': validated_data.get('last_name', instance.user.last_name),
        'email': validated_data.get('email', instance.user.email),
        'password': validated_data.get('password', instance.user.password),  
    } 
   
     user_instance = instance.user
     user_instance.first_name = user_data['first_name']
     user_instance.middle_name = user_data['middle_name']
     user_instance.last_name = user_data['last_name']
     user_instance.email = user_data['email']
     user_instance.set_password(validated_data.get('password')) 
  
     try:
        user_instance.save()
        instance.save()  
     except IntegrityError:
        raise serializers.ValidationError("user with this email does not exist")
     
     return instance
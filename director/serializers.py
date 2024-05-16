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
    

class TermSerializer(serializers.ModelSerializer):
        year = serializers.PrimaryKeyRelatedField(queryset = SchoolYear.objects.all())

        class Meta:
            model = Term
            fields = ['id','year', 'term_number', 'start_date', 'end_date']

        def to_representation(self, instance):
            representation = super().to_representation(instance)
            representation['year'] = instance.year.year_name
            return representation
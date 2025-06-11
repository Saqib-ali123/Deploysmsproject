from rest_framework import serializers

from authentication.models import User
from director.models import Address, City, Country, Role, ClassPeriod, State
from .models import GuardianType, Student, StudentGuardian,StudentYearLevel
from director.models import ClassPeriod, YearLevel



from django.db import IntegrityError
from django.core.exceptions import MultipleObjectsReturned

from .models import Guardian
from director.models import BankingDetail


class GuardianTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardianType
        fields = "__all__"
        
# class StudentYearLevelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StudentYearLevel
#         fields = "__all__"



class StudentYearLevelSerializer(serializers.ModelSerializer):
   
    student = serializers.SerializerMethodField(read_only=True)
    level = serializers.SerializerMethodField(read_only=True)

    
    level_id = serializers.PrimaryKeyRelatedField(
        queryset=YearLevel.objects.all(),
        write_only=True,
        source='level'
    )

    class Meta:
        model = StudentYearLevel
        fields = ['id', 'student',  'level', 'level_id', 'year']

    def get_student(self, obj):
        user = obj.student.user
        return {
            "id": obj.student.id,
            "first_name": user.first_name if user else "",
            "last_name": user.last_name if user else "",
            # "email": user.email if user else ""
        }


    def get_level(self, obj):
        return {
            "id": obj.level.id,
            "name": obj.level.level_name
        }



class StudentSerializer(serializers.ModelSerializer):
    # User Info (write-only)
    first_name = serializers.CharField(max_length=100, write_only=True)
    middle_name = serializers.CharField(max_length=100, write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100, write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(max_length=100, write_only=True, required=False)
    user_profile = serializers.ImageField(required=False, allow_null=True, write_only=True)

    # Student Fields
    father_name = serializers.CharField(required=False, allow_blank=True)
    mother_name = serializers.CharField(required=False, allow_blank=True)
    religion = serializers.CharField(required=False, allow_blank=True)
    category = serializers.ChoiceField(
        choices=[('SC', 'Scheduled Caste'), ('ST', 'Scheduled Tribe'), ('OBC', 'Other Backward Class'), ('GEN', 'General')],
        required=False
    )
    height = serializers.FloatField(required=False)
    weight = serializers.FloatField(required=False)
    blood_group = serializers.CharField(required=False, allow_blank=True)
    number_of_siblings = serializers.IntegerField(required=False)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender = serializers.CharField(required=False, allow_blank=True)
    # enrolment_date = serializers.DateField(required=False, allow_null=True)

    classes = serializers.PrimaryKeyRelatedField(queryset=ClassPeriod.objects.all(), many=True, required=False)

    # Address fields for input (write_only)
    house_no = serializers.CharField(required=False, allow_blank=True, write_only=True)
    habitation = serializers.CharField(required=False, allow_blank=True, write_only=True)
    word_no = serializers.CharField(required=False, allow_blank=True, write_only=True)
    zone_no = serializers.CharField(required=False, allow_blank=True, write_only=True)
    block = serializers.CharField(required=False, allow_blank=True, write_only=True)
    district = serializers.CharField(required=False, allow_blank=True, write_only=True)
    division = serializers.CharField(required=False, allow_blank=True, write_only=True)
    area_code = serializers.CharField(required=False, allow_blank=True, write_only=True)
    address_line = serializers.CharField(required=False, allow_blank=True, write_only=True)
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), required=False, write_only=True)
    state = serializers.PrimaryKeyRelatedField(queryset=State.objects.all(), required=False, write_only=True)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), required=False, write_only=True)

    # Banking fields for input (write_only)
    account_no = serializers.CharField(required=False, allow_blank=True, write_only=True)
    ifsc_code = serializers.CharField(required=False, allow_blank=True, write_only=True)
    holder_name = serializers.CharField(required=False, allow_blank=True, write_only=True)

    # For output: Address and Banking details shown as nested objects
    address = serializers.SerializerMethodField()
    banking_detail = serializers.SerializerMethodField()

    class Meta:
        model = Student
        exclude = ['user']  # user handled separately

    def get_address(self, obj):
        address = Address.objects.filter(user=obj.user).first()
        if address:
            return {
                "house_no": address.house_no,
                "habitation": address.habitation,
                "word_no": address.word_no,
                "zone_no": address.zone_no,
                "block": address.block,
                "district": address.district,
                "division": address.division,
                "area_code": address.area_code,
                "address_line": address.address_line,
                "country": address.country.id if address.country else None,
                "state": address.state.id if address.state else None,
                "city": address.city.id if address.city else None,
            }
        return None

    def get_banking_detail(self, obj):
        banking = getattr(obj.user, 'bankingdetail', None)
        if banking:
            return {
                "account_no": banking.account_no,
                "ifsc_code": banking.ifsc_code,
                "holder_name": banking.holder_name,
            }
        return None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        user = instance.user
        rep['first_name'] = user.first_name
        rep['middle_name'] = user.middle_name
        rep['last_name'] = user.last_name
        rep['email'] = user.email
        rep['user_profile'] = user.user_profile.url if user.user_profile else None

        # Add nested address and banking data
        rep['address'] = self.get_address(instance)
        rep['banking_detail'] = self.get_banking_detail(instance)

        return rep

    def create(self, validated_data):
        from director.serializers import BankingDetailsSerializer
        # Extract user data
        user_data = {
            'first_name': validated_data.pop('first_name', ''),
            'middle_name': validated_data.pop('middle_name', ''),
            'last_name': validated_data.pop('last_name', ''),
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password', None),
            'user_profile': validated_data.pop('user_profile', None),
        }

        classes_data = validated_data.pop('classes', [])

        # Extract address data
        address_data = {
            'house_no': validated_data.pop('house_no', None),
            'habitation': validated_data.pop('habitation', None),
            'word_no': validated_data.pop('word_no', None),
            'zone_no': validated_data.pop('zone_no', None),
            'block': validated_data.pop('block', None),
            'district': validated_data.pop('district', None),
            'division': validated_data.pop('division', None),
            'area_code': validated_data.pop('area_code', None),
            'address_line': validated_data.pop('address_line', None),
            'country': validated_data.pop('country', None),
            'state': validated_data.pop('state', None),
            'city': validated_data.pop('city', None),
        }
        address_data = {k: v for k, v in address_data.items() if v is not None}

        # Extract banking data
        banking_data = {
            'account_no': validated_data.pop('account_no', None),
            'ifsc_code': validated_data.pop('ifsc_code', None),
            'holder_name': validated_data.pop('holder_name', None),
        }
        banking_data = {k: v for k, v in banking_data.items() if v is not None}

        # Check for existing user email
        if User.objects.filter(email=user_data['email']).exists():
            raise serializers.ValidationError("User with this email already exists.")

        # Create User
        role, _ = Role.objects.get_or_create(name='student')
        user = User.objects.create_user(**user_data)
        user.role.add(role)

        # Create Address
        if address_data:
            address_data['user'] = user
            Address.objects.create(**address_data)

        # Create Banking Details
        if banking_data:
            banking_data['user'] = user
            banking_serializer = BankingDetailsSerializer(data=banking_data, context={'user': user})
            banking_serializer.is_valid(raise_exception=True)
            banking_serializer.save()

        # Create Student
        student = Student.objects.create(user=user, **validated_data)
        student.classes.set(classes_data)

        return student



class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name"]





class GuardianSerializer(serializers.ModelSerializer):
    # User Info (write_only on input)
    first_name = serializers.CharField(max_length=100, write_only=True)
    middle_name = serializers.CharField(max_length=100, write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100, write_only=True)
    password = serializers.CharField(max_length=100, write_only=True, required=False)
    email = serializers.EmailField(write_only=True)
    user_profile = serializers.ImageField(required=False, allow_null=True, write_only=True)
    
    # Guardian Fields (include here)
    phone_no = serializers.CharField(max_length=50)
    annual_income = serializers.IntegerField()
    means_of_livelihood = serializers.ChoiceField(choices=[('Govt', 'Government'), ('Non-Govt', 'Non-Government')], default='Govt')
    qualification = serializers.CharField(max_length=300)
    occupation = serializers.CharField(max_length=300)
    designation = serializers.CharField(max_length=300)

    class Meta:
        model = Guardian
        exclude = ["user"]

    def create(self, validated_data):
        user_data = {
            "first_name": validated_data.pop("first_name"),
            "middle_name": validated_data.pop("middle_name", ""),
            "last_name": validated_data.pop("last_name"),
            "password": validated_data.pop("password", None),
            "email": validated_data.pop("email"),
            "user_profile": validated_data.pop("user_profile", None),
        }

        phone_no = validated_data.pop('phone_no')
        annual_income = validated_data.pop('annual_income')
        means_of_livelihood = validated_data.pop('means_of_livelihood', 'Govt')
        qualification = validated_data.pop('qualification')
        occupation = validated_data.pop('occupation')
        designation = validated_data.pop('designation')

        if User.objects.filter(email=user_data["email"]).exists():
            raise serializers.ValidationError("User with this email already exists.")

        role, _ = Role.objects.get_or_create(name='guardian')
        user = User.objects.create_user(**user_data)
        user.role.add(role)

        guardian = Guardian.objects.create(
            user=user,
            phone_no=phone_no,
            annual_income=annual_income,
            means_of_livelihood=means_of_livelihood,
            qualification=qualification,
            occupation=occupation,
            designation=designation,
            **validated_data
        )

        return guardian

    def update(self, instance, validated_data):
        user = instance.user

        # Update user fields
        user.first_name = validated_data.get('first_name', user.first_name)
        user.middle_name = validated_data.get('middle_name', user.middle_name)
        user.last_name = validated_data.get('last_name', user.last_name)
        password = validated_data.get('password', None)
        if password:
            user.set_password(password)
        user.email = validated_data.get('email', user.email)
        user_profile = validated_data.get('user_profile', None)
        if user_profile is not None:
            user.user_profile = user_profile
        user.save()

        # Update guardian fields
        instance.phone_no = validated_data.get('phone_no', instance.phone_no)
        instance.annual_income = validated_data.get('annual_income', instance.annual_income)
        instance.means_of_livelihood = validated_data.get('means_of_livelihood', instance.means_of_livelihood)
        instance.qualification = validated_data.get('qualification', instance.qualification)
        instance.occupation = validated_data.get('occupation', instance.occupation)
        instance.designation = validated_data.get('designation', instance.designation)
        instance.save()

        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        user = instance.user
        rep.update({
            "first_name": user.first_name,
            "middle_name": user.middle_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_no": instance.phone_no,
            "annual_income": instance.annual_income,
            "means_of_livelihood": instance.means_of_livelihood,
            "qualification": instance.qualification,
            "occupation": instance.occupation,
            "designation": instance.designation,
            "user_profile": user.user_profile.url if user.user_profile else None,
        })
        return rep






    
#     class Meta:
#         model = Guardian
#         exclude = ["user"]
#     #     extra_kwargs = {
#     # 'password': {'write_only': True},
#         # }    
        

## As of 29May25 at 02:30 PM
class StudentYearLevelSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    level_name = serializers.CharField(source='level.level_name', read_only=True)
    year_name = serializers.CharField(source='year.year_name', read_only=True)

    def get_student_name(self, obj):
        first_name = obj.student.user.first_name or ''
        last_name = obj.student.user.last_name or ''
        return f"{first_name} {last_name}".strip()

    class Meta:
        model = StudentYearLevel
        fields = ['id', 'student_name', 'level_name', 'year_name']


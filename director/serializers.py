from rest_framework import serializers
from .models import *
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError
from student.serializers import *
# from authentication.serializers import UserSerializer
from uuid import uuid4


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


class BankingDetailsSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(max_length=250, write_only=True)

    class Meta:
        model = BankingDetail
        fields = ["email", "account_no", "ifsc_code", "holder_name"]

    def create(self, validated_data):
        user_data = {"email": validated_data.pop("email")}
        user = User.objects.filter(email=user_data["email"]).first()
        if user:

            banking_details = BankingDetail.objects.create(user=user, **validated_data)
            return banking_details
        else:
            raise serializers.ValidationError("User does not exists")

    def update(self, instance, validated_data):
        instance.user.email = validated_data.get("email", User.email)
        instance.account_no = validated_data.get("account_no", instance.account_no)
        instance.ifsc_code = validated_data.get("ifsc_code", instance.ifsc_code)
        instance.holder_name = validated_data.get("holder_name", instance.holder_name)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update(
            {
                "first_name": instance.user.first_name,
                "middle_name": instance.user.middle_name,
                "last_name": instance.user.last_name,
                "email": instance.user.email,
                "account_no": instance.account_no,
                "ifsc_code": instance.ifsc_code,
                "holder_name": instance.holder_name,
            }
        )
        return representation


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name"]

    def create_or_get_role(self, role_name):
        existing_role = Role.objects.filter(name=role_name).first()
        if existing_role:
            return existing_role
        else:
            new_role = Role.objects.create(name=role_name)
            return new_role


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = "__all__"


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


# class AddressSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Address
#         exclude = ["user"]

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         representation["country"] = instance.country.name
#         representation["state"] = instance.state.name
#         representation["city"] = instance.city.name
#         return representation

# Added as of 28April25

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

    def validate(self, add):
        user = add.get('user')
        house_no = add.get('house_no')
        area_code = add.get('area_code')
        country = add.get('country')
        state = add.get('state')
        city = add.get('city')
        address_line = add.get('address_line')

        # Address exists
        if Address.objects.filter(
            user=user,
            house_no=house_no,
            area_code=area_code,
            country=country,
            state=state,
            city=city,
            address_line=address_line
        ).exists():
            raise serializers.ValidationError("Address already exists for the user.")

        return add



class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolYear
        fields = "__all__"


class PeriodSerializer(serializers.ModelSerializer):
    year = serializers.PrimaryKeyRelatedField(queryset=SchoolYear.objects.all())

    class Meta:
        model = Period
        fields = ["year", "name", "start_period_time", "end_period_time"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            representation["year"] = instance.year.year_name
        except AttributeError:
            representation["year"] = None
        return representation


class TermSerializer(serializers.ModelSerializer):
    year = serializers.PrimaryKeyRelatedField(queryset=SchoolYear.objects.all())

    class Meta:
        model = Term
        fields = ["id", "year", "term_number", "start_date", "end_date"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["year"] = instance.year.year_name
        return representation


class DirectorProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=100, write_only=True)
    middle_name = serializers.CharField(
        max_length=100, write_only=True, allow_blank=True, required=False
    )
    last_name = serializers.CharField(max_length=100, write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Director
        exclude = ["user"]

    def create(self, validated_data):

        user_data = {
            "first_name": validated_data.pop("first_name"),
            "middle_name": validated_data.pop("middle_name", ""),
            "last_name": validated_data.pop("last_name"),
            "email": validated_data.pop("email"),
            "password": validated_data.pop("password"),
        }
        try:
            role, created = Role.objects.get_or_create(name="director")

        except MultipleObjectsReturned:
            raise serializers.ValidationError("Something went wrong")

        user = User.objects.filter(email=user_data["email"]).first()
        if user:

            if not user.role.filter(name="director").exists():
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
            "first_name": instance.user.first_name,
            "middle_name": instance.user.middle_name,
            "last_name": instance.user.last_name,
            "email": instance.user.email,
        }
        representation.update(data)
        return representation

    def update(self, instance, validated_data):

        user_data = {
            "first_name": validated_data.get("first_name", instance.user.first_name),
            "middle_name": validated_data.get("middle_name", instance.user.middle_name),
            "last_name": validated_data.get("last_name", instance.user.last_name),
            "email": validated_data.get("email", instance.user.email),
            "password": validated_data.get("password", instance.user.password),
        }

        user_instance = instance.user
        user_instance.first_name = user_data["first_name"]
        user_instance.middle_name = user_data["middle_name"]
        user_instance.last_name = user_data["last_name"]
        user_instance.email = user_data["email"]
        user_instance.set_password(validated_data.get("password"))

        try:
            user_instance.save()
            instance.save()
        except IntegrityError:
            raise serializers.ValidationError("user with this email does not exist")

        return instance


class AdmissionSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    guardian = GuardianSerializer()

    class Meta:
        model = Admission
        fields = "__all__"

    def create(self, validated_data):

        student_data = validated_data.pop("student")
        guardian_data = validated_data.pop("guardian")

        student = StudentSerializer(data=student_data)
        if student.is_valid():
            student = student.save()
        else:
            raise serializers.ValidationError(student.errors)

        guardian = GuardianSerializer(data=guardian_data)
        if guardian.is_valid():
            guardian = guardian.save()
        else:
            raise serializers.ValidationError(guardian.errors)

        admission = Admission.objects.create(
            student=student, guardian=guardian, **validated_data
        )

        return admission
    
    
    # admission update here
    
    def update(self, instance, validated_data):
        student_data = validated_data.pop("student", None)
        guardian_data = validated_data.pop("guardian", None)

        if student_data:
            student_serializer = StudentSerializer(instance.student, data=student_data)
            student_serializer.is_valid(raise_exception=True)
            student_serializer.save()

        if guardian_data:
            guardian_serializer = GuardianSerializer(instance.guardian, data=guardian_data)
            guardian_serializer.is_valid(raise_exception=True)
            guardian_serializer.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


# As of 05May25 at 01:00 PM
class ClassPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassPeriod
        fields = ['id','subject','teacher','term','start_time','end_time','classroom','name']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['start_time'] = instance.start_time.start_period_time.strftime('%I:%M %p')
        representation['end_time'] = instance.end_time.end_period_time.strftime('%I:%M %p')
        return representation
    

# As of 08may25 at 11:41 AM

# class FeeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Fee
#         fields = '__all__'

#     def validate_total_fee(self, value):
#         if value <= 0:
#             raise serializers.ValidationError("Total fee must be greater than zero.")
#         return value

#     def validate(self, data):
#         # Check if term and year_level are provided
#         if not data.get('term'):
#             raise serializers.ValidationError({"term": "Term is required."})
#         if not data.get('year_level'):
#             raise serializers.ValidationError({"year_level": "Year level is required."})
#         return data

#     def create(self, validated_data):
#         student = validated_data.get('student')
#         banking_detail = validated_data.get('banking_detail')

#         if banking_detail and student.user != banking_detail.user:
#             raise serializers.ValidationError("Banking detail does not match student.")

        # return super().create(validated_data)
        

# Fee submit serializer commented as of 12May25 at 02:44 PM
# class FeeSerializer(serializers.ModelSerializer):
#     student_id = serializers.IntegerField(write_only=True)
#     account_no = serializers.IntegerField(write_only=True)
#     term_id = serializers.IntegerField(write_only=True)
#     year_level_id = serializers.IntegerField(write_only=True)
#     amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2)#,write_only=True)

#     class Meta:
#         model = Fee
#         fields = [
#             'student_id', 'account_no', 'term_id', 'year_level_id',
#             'total_fee', 'amount_paid', 'payment_mode', 'remarks', 'receipt_number'
#         ]
#         read_only_fields = ['receipt_number']

#     def create(self, validated_data):
#         student_id = validated_data.pop('student_id')
#         account_no = validated_data.pop('account_no')
#         term_id = validated_data.pop('term_id')
#         year_level_id = validated_data.pop('year_level_id')
#         amount_paid = validated_data.pop('amount_paid')

#         try:
#             student = Student.objects.get(id=student_id)
#         except Student.DoesNotExist:
#             raise serializers.ValidationError({"student_id": "Student not found."})

#         try:
#             banking_detail = BankingDetail.objects.get(account_no=account_no)
#         except BankingDetail.DoesNotExist:
#             raise serializers.ValidationError({"account_no": "Banking detail not found."})

#         if banking_detail.user != student.user:
#             raise serializers.ValidationError("Banking detail not found for the student.")

#         try:
#             term = Term.objects.get(id=term_id)
#         except Term.DoesNotExist:
#             raise serializers.ValidationError({"term_id": "Term not found."})

#         try:
#             year_level = YearLevel.objects.get(id=year_level_id)
#         except YearLevel.DoesNotExist:
#             raise serializers.ValidationError({"year_level_id": "Year level not found."})

#         receipt_number = str(uuid4())

#         fee = Fee.objects.create(
#             student=student,
#             banking_detail=banking_detail,
#             term=term,
#             year_level=year_level,
#             total_fee=validated_data['total_fee'],
#             amount_paid=amount_paid,
#             payment_mode=validated_data['payment_mode'],
#             remarks=validated_data.get('remarks', ''),
#             receipt_number=receipt_number
#         )

#         # Add balance_amount to context/response if needed
#         fee.balance_amount = float(fee.total_fee) - float(amount_paid)
#         return fee

#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         data['student'] = f"{instance.student.user.first_name} {instance.student.user.last_name}"
#         data['banking_detail'] = instance.banking_detail.account_no
#         data['term'] = instance.term.term_number if instance.term else None
#         data['year_level'] = instance.year_level.level_name if instance.year_level else None
#         # data['amount_paid'] = instance.fee.amount_paid if instance.amount_paid else None
#         # data['balance_amount'] = float(instance.total_fee) - float(self.amount_paid)
#         data['amount_paid'] = float(instance.amount_paid) if instance.amount_paid is not None else 0.0
#         data['balance_amount'] = float(instance.total_fee) - float(instance.amount_paid or 0)

#         return data


class FeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeType
        fields = ['id', 'name', 'description']
        
        
class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = ['id', 'year_level', 'term', 'fee_type','total_fee']
        

class FeeSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = [
            'id', 'student', 'fee_structure', 'fee_type',
            'amount_paid', 'payment_mode', 'remarks','receipt_number'
        ]


from datetime import date
from rest_framework import serializers
from .models import *
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError
from student.serializers import *
# from authentication.serializers import UserSerializer
from uuid import uuid4
from django.utils import timezone
from decimal import Decimal
from collections import defaultdict
from django.db.models import Max



class YearLevelSerializer(serializers.ModelSerializer):   # coomented as of 05June25 at 01:36 AM
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
        
        
class ClassPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassPeriod
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


        # exclude = ["user"]

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation["country"] = instance.country.name
    #     representation["state"] = instance.state.name
    #     representation["city"] = instance.city.name
    #     return representation
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
        fields = ["id","year", "name", "start_period_time", "end_period_time"]

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
    middle_name = serializers.CharField(max_length=100, write_only=True, allow_blank=True, required=False)
    last_name = serializers.CharField(max_length=100, write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    user_profile = serializers.ImageField(required=False, allow_null=True, write_only=True)

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
            "user_profile": validated_data.pop("user_profile", None),
        }

        try:
            role, _ = Role.objects.get_or_create(name="director")
        except MultipleObjectsReturned:
            raise serializers.ValidationError("Multiple 'director' roles exist. Please fix your roles table.")

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
            raise serializers.ValidationError("User with this email already exists.")

        return director_profile

    def update(self, instance, validated_data):
        user = instance.user

        user.first_name = validated_data.get("first_name", user.first_name)
        user.middle_name = validated_data.get("middle_name", user.middle_name)
        user.last_name = validated_data.get("last_name", user.last_name)
        user.email = validated_data.get("email", user.email)

        if "password" in validated_data:
            user.set_password(validated_data["password"])

        if "user_profile" in validated_data:
            user.user_profile = validated_data.get("user_profile")

        try:
            user.save()
            instance.save()
        except IntegrityError:
            raise serializers.ValidationError("Failed to update. Email may already exist.")

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({
            "first_name": instance.user.first_name,
            "middle_name": instance.user.middle_name,
            "last_name": instance.user.last_name,
            "email": instance.user.email,
            "user_profile": instance.user.user_profile.url if instance.user.user_profile else None,
        })
        return representation


# class AdmissionSerializer(serializers.ModelSerializer):
#     student = StudentSerializer()
#     guardian = GuardianSerializer()

#     class Meta:
#         model = Admission
#         fields = "__all__"

#     def create(self, validated_data):

#         student_data = validated_data.pop("student")
#         guardian_data = validated_data.pop("guardian")

#         student = StudentSerializer(data=student_data,context={**self.context, "exclude_classes": True})
#         if student.is_valid():
#             student = student.save()
#         else:
#             raise serializers.ValidationError(student.errors)

#         guardian = GuardianSerializer(data=guardian_data)
#         if guardian.is_valid():
#             guardian = guardian.save()
#         else:
#             raise serializers.ValidationError(guardian.errors)

#         admission = Admission.objects.create(
#             student=student, guardian=guardian, **validated_data
#         )

#         return admission
# /////////////////correct////////////////////

# class AdmissionSerializer(serializers.ModelSerializer):
#     student = StudentSerializer()
#     guardian = GuardianSerializer()

#     class Meta:
#         model = Admission
#         fields = "__all__"

#     def create(self, validated_data):
#         student_data = validated_data.pop("student")
#         guardian_data = validated_data.pop("guardian")

#         # Extract and handle class assignments
#         classes_data = student_data.pop("classes", [])

#         # Handle student
#         student_email = student_data.get("email")
#         student = Student.objects.filter(user__email__iexact=student_email).first()
#         if not student:
#             student_serializer = StudentSerializer(data={**student_data, "classes": classes_data})
#             student_serializer.is_valid(raise_exception=True)
#             student = student_serializer.save()
#         else:
#             if classes_data:
#                 student.classes.set(classes_data)

#         # Handle guardian
#         guardian_email = guardian_data.get("email")
#         guardian = Guardian.objects.filter(user__email__iexact=guardian_email).first()
#         if not guardian:
#             guardian_serializer = GuardianSerializer(data=guardian_data)
#             guardian_serializer.is_valid(raise_exception=True)
#             guardian = guardian_serializer.save()

#         # Create admission record
#         admission = Admission.objects.create(
#             student=student,
#             guardian=guardian,
#             **validated_data
#         )

#         return admission

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)

#         # Student representation
#         student = instance.student
#         student_user = student.user
#         representation.update({
#             "student_first_name": student_user.first_name,
#             "student_middle_name": student_user.middle_name,
#             "student_last_name": student_user.last_name,
#             "student_email": student_user.email,
#             "student_date_of_birth": student.date_of_birth,
#             "student_gender": student.gender,
#             "student_enrolment_date": student.enrolment_date,
#             "student_classes": [cls.name for cls in student.classes.all()],
#         })

#         # Guardian representation
#         guardian = instance.guardian
#         guardian_user = guardian.user
#         representation.update({
#             "guardian_first_name": guardian_user.first_name,
#             "guardian_middle_name": guardian_user.middle_name,
#             "guardian_last_name": guardian_user.last_name,
#             "guardian_email": guardian_user.email,
#             "guardian_phone_no": guardian.phone_no,
#         })

#         # Use display names for foreign keys
#         representation["year_level"] = instance.year_level.level_name if instance.year_level else None
#         representation["school_year"] = instance.school_year.year_name if instance.school_year else None

#         # Remove nested original fields
#         representation.pop("student", None)
#         representation.pop("guardian", None)

#         return representation



# class AdmissionSerializer(serializers.ModelSerializer):
#     student = StudentSerializer(write_only=True)
#     guardian = GuardianSerializer(write_only=True)

#     class Meta:
#         model = Admission
#         fields = "__all__"

#     def create(self, validated_data):
#         student_data = validated_data.pop("student")
#         guardian_data = validated_data.pop("guardian")

#         # Extract and remove classes from student data
#         classes_data = student_data.pop("classes", [])

#         # Remove password if it's empty or not included
#         # student_data.pop("password", None)
#         # guardian_data.pop("password", None)

#         # --- Handle student ---
#         student_email = student_data.get("email")
#         student = Student.objects.filter(user__email__iexact=student_email).first()

#         if not student:
#             student_serializer = StudentSerializer(data={**student_data, "classes": classes_data})
#             student_serializer.is_valid(raise_exception=True)
#             student = student_serializer.save()
#         else:
#             if classes_data:
#                 student.classes.set(classes_data)

#         # --- Handle guardian ---
#         guardian_email = guardian_data.get("email")
#         guardian = Guardian.objects.filter(user__email__iexact=guardian_email).first()

#         if not guardian:
#             guardian_serializer = GuardianSerializer(data=guardian_data)
#             guardian_serializer.is_valid(raise_exception=True)
#             guardian = guardian_serializer.save()

#         # --- Create admission record ---
#         admission = Admission.objects.create(
#             student=student,
#             guardian=guardian,
#             **validated_data
#         )

#         # Link student to year level
#         from student.models import StudentYearLevel
#         StudentYearLevel.objects.get_or_create(
#             student=student,
#             level=admission.year_level,
#             year=admission.school_year
#         )

#         return admission
    
    
#     # admission update here
    
#     def update(self, instance, validated_data):
#         student_data = validated_data.pop("student", None)
#         guardian_data = validated_data.pop("guardian", None)

#         if student_data:
#             student_serializer = StudentSerializer(instance.student, data=student_data)
#             student_serializer.is_valid(raise_exception=True)
#             student_serializer.save()

#         if guardian_data:
#             guardian_serializer = GuardianSerializer(instance.guardian, data=guardian_data)
#             guardian_serializer.is_valid(raise_exception=True)
#             guardian_serializer.save()

#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()

#         return instance


# **************Add guardin type***************

# class AdmissionSerializer(serializers.ModelSerializer):
#     student = StudentSerializer(write_only=True)
#     guardian = GuardianSerializer(write_only=True)

#     class Meta:
#         model = Admission
#         fields = "__all__"

#     def create(self, validated_data):
#         student_data = validated_data.pop("student")
#         guardian_data = validated_data.pop("guardian")
#         classes_data = student_data.pop("classes", [])

#         student_email = student_data.get("email")
#         student = Student.objects.filter(user__email__iexact=student_email).first()

#         if not student:
#             student_serializer = StudentSerializer(data={**student_data, "classes": classes_data})
#             student_serializer.is_valid(raise_exception=True)
#             student = student_serializer.save()
#         else:
#             if classes_data:
#                 student.classes.set(classes_data)

#         guardian_email = guardian_data.get("email")
#         guardian = Guardian.objects.filter(user__email__iexact=guardian_email).first()

#         if not guardian:
#             guardian_serializer = GuardianSerializer(data=guardian_data)
#             guardian_serializer.is_valid(raise_exception=True)
#             guardian = guardian_serializer.save()

#         admission = Admission.objects.create(
#             student=student,
#             guardian=guardian,
#             **validated_data
#         )

#         from student.models import StudentYearLevel
#         StudentYearLevel.objects.get_or_create(
#             student=student,
#             level=admission.year_level,
#             year=admission.school_year
#         )

#         return admission

#     def update(self, instance, validated_data):
#         student_data = validated_data.pop("student", None)
#         guardian_data = validated_data.pop("guardian", None)

#         if student_data:
#             student_serializer = StudentSerializer(instance.student, data=student_data)
#             student_serializer.is_valid(raise_exception=True)
#             student_serializer.save()

#         if guardian_data:
#             guardian_serializer = GuardianSerializer(instance.guardian, data=guardian_data)
#             guardian_serializer.is_valid(raise_exception=True)
#             guardian_serializer.save()

#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()

#         return instance

    
#     def to_representation(self, instance):
#         rep = super().to_representation(instance)

#         student = instance.student
#         guardian = instance.guardian

#         # Student info
#         rep["student_first_name"] = student.user.first_name
#         rep["student_middle_name"] = student.user.middle_name if hasattr(student.user, 'middle_name') else ""
#         rep["student_last_name"] = student.user.last_name
#         rep["student_email"] = student.user.email
#         rep["student_date_of_birth"] = student.date_of_birth
#         rep["student_gender"] = student.gender
#         rep["student_enrolment_date"] = student.enrolment_date
#         rep["student_classes"] = [cls.name for cls in student.classes.all()]

#         # Guardian info
#         rep["guardian_first_name"] = guardian.user.first_name
#         rep["guardian_middle_name"] = guardian.user.middle_name if hasattr(guardian.user, 'middle_name') else ""
#         rep["guardian_last_name"] = guardian.user.last_name
#         rep["guardian_email"] = guardian.user.email
#         rep["guardian_phone_no"] = guardian.phone_no

#         # Optional: readable fields
#         rep["year_level"] = instance.year_level.level_name if instance.year_level else None
#         rep["school_year"] = instance.school_year.year_name if instance.school_year else None

#         # Remove original nested keys
#         rep.pop("student", None)
#         rep.pop("guardian", None)

#         return rep


# ***************guardin type *****************
class AdmissionSerializer(serializers.ModelSerializer):
    student = StudentSerializer(write_only=True)
    guardian = GuardianSerializer(write_only=True)
    guardian_type = serializers.PrimaryKeyRelatedField(
        queryset=GuardianType.objects.all(), write_only=True
    )

    class Meta:
        model = Admission
        fields = "__all__"  

    def create(self, validated_data):
        student_data = validated_data.pop("student")
        guardian_data = validated_data.pop("guardian")
        guardian_type = validated_data.pop("guardian_type")

        classes_data = student_data.pop("classes", [])

        # --- Student Creation/Link ---
        student_email = student_data.get("email")
        student = Student.objects.filter(user__email__iexact=student_email).first()

        if not student:
            student_serializer = StudentSerializer(data={**student_data, "classes": classes_data})
            student_serializer.is_valid(raise_exception=True)
            student = student_serializer.save()
        else:
            if classes_data:
                student.classes.set(classes_data)

        # --- Guardian Creation/Link ---
        guardian_email = guardian_data.get("email")
        guardian = Guardian.objects.filter(user__email__iexact=guardian_email).first()

        if not guardian:
            guardian_serializer = GuardianSerializer(data=guardian_data)
            guardian_serializer.is_valid(raise_exception=True)
            guardian = guardian_serializer.save()

        # --- Create Admission ---
        admission = Admission.objects.create(
            student=student,
            guardian=guardian,
            **validated_data
        )

        # --- Create StudentGuardian Relationship ---
        StudentGuardian.objects.get_or_create(
            student=student,
            guardian=guardian,
            guardian_type=guardian_type
        )

        # --- Optional: Track Year Level ---
        from student.models import StudentYearLevel
        StudentYearLevel.objects.get_or_create(
            student=student,
            level=admission.year_level,
            year=admission.school_year
        )

        return admission

    def update(self, instance, validated_data):
        student_data = validated_data.pop("student", None)
        guardian_data = validated_data.pop("guardian", None)
        guardian_type = validated_data.pop("guardian_type", None)

        if student_data:
            student_serializer = StudentSerializer(instance.student, data=student_data)
            student_serializer.is_valid(raise_exception=True)
            student_serializer.save()

        if guardian_data:
            guardian_serializer = GuardianSerializer(instance.guardian, data=guardian_data)
            guardian_serializer.is_valid(raise_exception=True)
            guardian_serializer.save()

        if guardian_type:
            StudentGuardian.objects.update_or_create(
                student=instance.student,
                guardian=instance.guardian,
                defaults={"guardian_type": guardian_type}
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        student = instance.student
        guardian = instance.guardian

        # Student details
        rep["student_first_name"] = student.user.first_name
        rep["student_middle_name"] = student.user.middle_name
        rep["student_last_name"] = student.user.last_name
        rep["student_email"] = student.user.email
        rep["student_date_of_birth"] = student.date_of_birth
        rep["student_gender"] = student.gender
        rep["student_enrolment_date"] = student.enrolment_date
        rep["student_classes"] = [cls.name for cls in student.classes.all()]

        # Guardian details
        rep["guardian_first_name"] = guardian.user.first_name
        rep["guardian_middle_name"] = guardian.user.middle_name
        rep["guardian_last_name"] = guardian.user.last_name
        rep["guardian_email"] = guardian.user.email
        rep["guardian_phone_no"] = guardian.phone_no

        # Guardian Type (Relationship)
        guardian_relation = StudentGuardian.objects.filter(
            student=student,
            guardian=guardian
        ).first()

        rep["guardian_type"] = guardian_relation.guardian_type.name if guardian_relation else None

        # Human-readable year/level
        rep["year_level"] = instance.year_level.level_name if instance.year_level else None
        rep["school_year"] = instance.school_year.year_name if instance.school_year else None

        # Clean output
        rep.pop("student", None)
        rep.pop("guardian", None)

        return rep



# **********Assignment ClassPeriod for Student behalf of YearLevel(Standard)********************

# As of 05May25 at 01:00 PM
from rest_framework import serializers
from director.models import ClassPeriod, YearLevel
from student.models import Student, StudentYearLevel


class ClassPeriodSerializer(serializers.ModelSerializer):
    # Extra fields for the custom POST action
    year_level_name = serializers.CharField(write_only=True, required=False)
    class_period_names = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    class Meta:
        model = ClassPeriod
        fields = [
            'id', 'subject', 'teacher', 'term',
            'start_time', 'end_time', 'classroom', 'name',
            'year_level_name', 'class_period_names'  
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['start_time'] = instance.start_time.start_period_time.strftime('%I:%M %p')
        representation['end_time'] = instance.end_time.end_period_time.strftime('%I:%M %p')
        return representation

    def create(self, validated_data):
        # Handle assignment logic only if year_level_name and class_period_names are present
        year_level_name = validated_data.pop('year_level_name', None)
        class_period_names = validated_data.pop('class_period_names', None)

        if year_level_name and class_period_names:
            try:
                year_level = YearLevel.objects.get(level_name=year_level_name)
            except YearLevel.DoesNotExist:
                raise serializers.ValidationError("Invalid YearLevel name.")

            class_periods = ClassPeriod.objects.filter(name__in=class_period_names)
            if class_periods.count() != len(class_period_names):
                raise serializers.ValidationError("Some ClassPeriod names are invalid.")

            student_ids = StudentYearLevel.objects.filter(level=year_level).values_list("student_id", flat=True)
            students = Student.objects.filter(id__in=student_ids)

            for student in students:
                student.classes.add(*class_periods)

            return {
                "students_updated": students.count(),
                "class_periods_assigned": [cp.name for cp in class_periods]
            }

        # If not an assignment request, create a regular ClassPeriod (fallback)
        return super().create(validated_data)


    
# As of 04June2025 at 12:15 AM
# Re-implementation of Fee module based on the provided fee card


# Added as of 06June25 at 02:50 PM

class FeeTypeSerializer(serializers.ModelSerializer):
    # name = serializers.SerializerMethodField()
    
    class Meta:
        model = FeeType
        fields = ['id', 'name']


class YearLevelFeeSerializer(serializers.ModelSerializer):
    year_level_name = serializers.SerializerMethodField()
    fee_type_name = serializers.SerializerMethodField()
    year_level_id = serializers.IntegerField(source='year_level.id', read_only=True)

    class Meta:
        model = YearLevelFee
        fields = ['id', 'year_level', 'fee_type', 'year_level_name', 'fee_type_name', 'amount', 'year_level_id']

    def get_year_level_name(self, obj):
        return obj.year_level.level_name

    def get_fee_type_name(self, obj):
        return obj.fee_type.name

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('year_level', None)
        data.pop('fee_type', None)
        return data
 
    # Added this as of 11June25 at 11:39 AM
    @staticmethod
    def group_by_year_level(fees):
        grouped_fees = {}
        for fee in fees:
            year_level_name = fee['year_level_name']
            year_level_id = fee['year_level_id']
            fee_data = {
                'id': fee['id'],
                'fee_type': fee['fee_type_name'],
                'amount': fee['amount']
            }

            # Use a tuple key to keep both id and name
            key = (year_level_id, year_level_name)

            if key not in grouped_fees:
                grouped_fees[key] = {
                    'id': year_level_id,
                    'year_level': year_level_name,
                    'fees': []
                }

            grouped_fees[key]['fees'].append(fee_data)

        return list(grouped_fees.values())



### just added to submit fee for multiple months as of 09Jun25 at 06:53 PM
class FeeRecordSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    student_id = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), source='student', write_only=True)
    year_level_fees = serializers.PrimaryKeyRelatedField(queryset=YearLevelFee.objects.all(), many=True, write_only=True)
    year_level_fees_grouped = serializers.SerializerMethodField(read_only=True)

    total_amount = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    paid_amount = serializers.DecimalField(max_digits=8, decimal_places=2)
    due_amount = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    late_fee = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    payment_date = serializers.DateField(read_only=True)
    receipt_number = serializers.CharField(read_only=True)
    payment_status = serializers.CharField(max_length=20, read_only=True)
    remarks = serializers.CharField(max_length=255)
    signature = serializers.CharField(max_length=100)
    
    payment_mode = serializers.ChoiceField(choices=FeeRecord._meta.get_field('payment_mode').choices)

    month = serializers.ChoiceField(choices=FeeRecord.MONTH_CHOICES)

    class Meta:
        model = FeeRecord
        fields = [
            'id', 'student', 'student_id', 'month', 'year_level_fees', 'year_level_fees_grouped',
            'total_amount', 'paid_amount', 'due_amount', 'payment_date', 'payment_mode', 'is_cheque_cleared','receipt_number',
            'late_fee', 'payment_status', 'remarks', 'signature'
        ]
        read_only_fields = ['receipt_number', 'payment_date', 'total_amount', 'due_amount', 'late_fee']

    def get_student(self, obj):
        return {
            "id": obj.student.id,
            "name": f"{obj.student.user.first_name} {obj.student.user.last_name}"
        }

    def get_year_level_fees_grouped(self, obj):
        grouped = defaultdict(list)
        for fee in obj.year_level_fees.all():
            year_level_name = fee.year_level.level_name
            grouped[year_level_name].append({
                "id": fee.id,
                "fee_type": fee.fee_type.name,
                "amount": str(fee.amount),
            })
        return [{"year_level": yl, "fees": fees} for yl, fees in grouped.items()]
    
    def validate(self, data):
        student = data.get('student')
        month = data.get('month')
        year_level_fees = data.get('year_level_fees', [])
        paid_amount = data.get('paid_amount', 0)
        # total_amount = data.get('total_amount',0)   # Added as of 09June25

        # Prevent duplicate fee entry for same student + month
        if self.instance is None:  # Only during creation
            if FeeRecord.objects.filter(student=student, month=month).exists():
                raise serializers.ValidationError(f"Fee already submitted for {month} for this student.")

        # Validate fees
        if not year_level_fees:
            raise serializers.ValidationError("At least one year level fee must be selected.")

        total = 0
        for fee in year_level_fees:
            total += fee.amount

        # caluculate total amount based on year level fee
        data['total_amount'] = total

        # calculate late fee, if submitted after 15th
        today = date.today()
        data['late_fee'] = 25 if today.day > 15 else 0
        
        # calculate due amount
        due = total + data['late_fee'] - paid_amount
        data['due_amount'] = due if due > 0 else 0
        
        # Determine payment status  commented as of 11June25
        # data['payment_status'] = 'Paid' if data['due_amount'] == 0 else 'Unpaid'

        return data
    
    ### Added this as of 11June25 at 01:39 PM
    def create(self, validated_data):
        year_level_fees = validated_data.pop('year_level_fees')
        validated_data['payment_date'] = date.today()

        total_amount = validated_data.get('total_amount', 0)
        paid_amount = validated_data.get('paid_amount', 0)
        late_fee = validated_data.get('late_fee', 0)
        due_amount = validated_data.get('due_amount', 0)
        payment_mode = validated_data.get('payment_mode')
        is_cheque_cleared = validated_data.get('is_cheque_cleared', False)

        # Default status
        payment_status = 'Unpaid'
        
        if payment_mode == 'Cash' or payment_mode == 'Online':
            if paid_amount >= total_amount + validated_data.get('late_fee', 0):
                payment_status = 'Paid'
        elif payment_mode == 'Cheque':
            if is_cheque_cleared and paid_amount >= total_amount + late_fee:
                payment_status = 'Paid'
            else:
                payment_status = 'Unpaid'
        
        validated_data['payment_status'] = payment_status

        fee_record = FeeRecord.objects.create(**validated_data)
        fee_record.year_level_fees.set(year_level_fees)
        return fee_record


### Razorpay Functionality Added as of 10Jun25

### Added as of 12june25 at 02:20 PM
class FeeRecordRazorpaySerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), source='student', write_only=True)
    year_level_fees = serializers.PrimaryKeyRelatedField(queryset=YearLevelFee.objects.all(), many=True)
    receipt_number = serializers.CharField(read_only=True)

    class Meta:
        model = FeeRecord
        fields = [
            'id', 'student_id', 'month', 'year_level_fees', 'total_amount', 'paid_amount', 'due_amount',
            'late_fee', 'payment_mode', 'payment_status', 'remarks', 'signature',
            'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature_id', 'receipt_number'
        ]
        read_only_fields = ['total_amount', 'due_amount', 'late_fee', 'payment_status',
                            'razorpay_payment_id', 'razorpay_signature_id', 'receipt_number']

    
    # just added as of 16June25 at 12:29 PM
    def validate(self, data):
        student = data.get('student')
        month = data.get('month')
        year_level_fees = data.get('year_level_fees', [])
        paid_amount = data.get('paid_amount', Decimal("0.00"))

        if not year_level_fees:
            raise serializers.ValidationError("At least one year level fee must be selected.")

        if FeeRecord.objects.filter(student=student, month=month).exists():
            raise serializers.ValidationError(f"Fee already submitted for {month} month for this student.")

        total = sum(fee.amount for fee in year_level_fees)
        late_fee = Decimal("25.00") if date.today().day > 15 else Decimal("0.00")
        due_amount = total + late_fee - paid_amount

        data['total_amount'] = total
        data['late_fee'] = late_fee
        data['due_amount'] = due_amount if due_amount > 0 else Decimal("0.00")

        # Extract Razorpay fields explicitly
        data['razorpay_order_id'] = self.initial_data.get('razorpay_order_id')
        data['razorpay_payment_id'] = self.initial_data.get('razorpay_payment_id')
        data['razorpay_signature_id'] = self.initial_data.get('razorpay_signature_id')

        return data         # just added as of 16June25 at 12:29 PM

    

    # just commented as of 13June25 at 04:23 PM as it is not saving Razorpay payment id,Razorpay signature id: in the FeeRecord DB
    
    def create(self, validated_data):      # just uncomment it as of 16June25 at 12:29 PM   
        year_level_fees = validated_data.pop('year_level_fees')
        validated_data['payment_date'] = date.today()

        total_amount = validated_data.get('total_amount', Decimal("0.00"))
        paid_amount = validated_data.get('paid_amount', Decimal("0.00"))
        late_fee = validated_data.get('late_fee', Decimal("0.00"))

        payment_status = 'Paid' if paid_amount >= (total_amount + late_fee) else 'Unpaid'
        validated_data['payment_status'] = payment_status

        fee_record = FeeRecord.objects.create(**validated_data)
        fee_record.year_level_fees.set(year_level_fees)
        return fee_record
    
    
    


    
   
    ### Added this as of 13June25 at 11:53 AM 
class RazorpayConfirmPaymentSerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature_id = serializers.CharField()




### Previous Razorpay Code commented as of 10June25
# class RazorpayPaymentInitiateSerializer(serializers.Serializer):
#     student_id = serializers.IntegerField()
#     fee_structure_id = serializers.IntegerField()
#     fee_type_id = serializers.IntegerField()
#     amount = serializers.DecimalField(max_digits=10, decimal_places=2)



# ********************OfficeStaffSerializer profile*******************************
class OfficeStaffSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=100, write_only=True)
    middle_name = serializers.CharField(max_length=100, write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100, write_only=True)
    password = serializers.CharField(max_length=100, write_only=True, required=False)
    email = serializers.EmailField(write_only=True)
    user_profile = serializers.ImageField(required=False, allow_null=True, write_only=True)

    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), many=True, required=False)
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all(), many=True, required=False)
    admissions = serializers.PrimaryKeyRelatedField(queryset=Admission.objects.all(), many=True, required=False)

    class Meta:
        model = OfficeStaff
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

        student_data = validated_data.pop("student", [])
        teacher_data = validated_data.pop("teacher", [])
        admissions_data = validated_data.pop("admissions", [])

        try:
            role, _ = Role.objects.get_or_create(name="office_staff")
        except MultipleObjectsReturned:
            raise serializers.ValidationError("Multiple roles named 'office_staff' found.")

        user = User.objects.filter(email=user_data["email"]).first()

        if user:
            if not user.role.filter(name="office_staff").exists():
                user.role.add(role)
                user.save()
            else:
                raise serializers.ValidationError("User with this email already exists and is an office staff.")
        else:
            user = User.objects.create_user(**user_data)
            user.role.add(role)
            user.save()

        office_staff = OfficeStaff.objects.create(user=user, **validated_data)
        office_staff.student.set(student_data)
        office_staff.teacher.set(teacher_data)
        office_staff.admissions.set(admissions_data)
        return office_staff

    def update(self, instance, validated_data):
        user = instance.user

        user.first_name = validated_data.pop("first_name", user.first_name)
        user.middle_name = validated_data.pop("middle_name", user.middle_name)
        user.last_name = validated_data.pop("last_name", user.last_name)
        user.email = validated_data.pop("email", user.email)
        if "password" in validated_data and validated_data["password"]:
            user.set_password(validated_data["password"])
        if "user_profile" in validated_data:
            user.user_profile = validated_data["user_profile"]

        user.save()

        instance.phone_no = validated_data.get("phone_no", instance.phone_no)
        instance.gender = validated_data.get("gender", instance.gender)
        instance.department = validated_data.get("department", instance.department)
        instance.save()

        if "student" in validated_data:
            instance.student.set(validated_data["student"])
        if "teacher" in validated_data:
            instance.teacher.set(validated_data["teacher"])
        if "admissions" in validated_data:
            instance.admissions.set(validated_data["admissions"])

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update({
            "first_name": instance.user.first_name,
            "middle_name": instance.user.middle_name,
            "last_name": instance.user.last_name,
            "email": instance.user.email,
            "user_profile": instance.user.user_profile.url if instance.user.user_profile else None,
        })

        # Remove relational fields from the output
        representation.pop("student", None)
        representation.pop("teacher", None)
        representation.pop("admissions", None)

        return representation
    
    
    
    # ******************DocumentTypeSerializer*************************
    
class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = "__all__" 
            
    
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields  = "__all__"      


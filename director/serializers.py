from rest_framework import serializers
from .models import *
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError
from student.serializers import *


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


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
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



class AdmissionSerializer(serializers.ModelSerializer):
    student = StudentSerializer(write_only=True)
    guardian = GuardianSerializer(write_only=True)

    class Meta:
        model = Admission
        fields = "__all__"

    def create(self, validated_data):
        student_data = validated_data.pop("student")
        guardian_data = validated_data.pop("guardian")

        # Extract and remove classes from student data
        classes_data = student_data.pop("classes", [])

        # Remove password if it's empty or not included
        # student_data.pop("password", None)
        # guardian_data.pop("password", None)

        # --- Handle student ---
        student_email = student_data.get("email")
        student = Student.objects.filter(user__email__iexact=student_email).first()

        if not student:
            student_serializer = StudentSerializer(data={**student_data, "classes": classes_data})
            student_serializer.is_valid(raise_exception=True)
            student = student_serializer.save()
        else:
            if classes_data:
                student.classes.set(classes_data)

        # --- Handle guardian ---
        guardian_email = guardian_data.get("email")
        guardian = Guardian.objects.filter(user__email__iexact=guardian_email).first()

        if not guardian:
            guardian_serializer = GuardianSerializer(data=guardian_data)
            guardian_serializer.is_valid(raise_exception=True)
            guardian = guardian_serializer.save()

        # --- Create admission record ---
        admission = Admission.objects.create(
            student=student,
            guardian=guardian,
            **validated_data
        )

        # Link student to year level
        from student.models import StudentYearLevel
        StudentYearLevel.objects.get_or_create(
            student=student,
            level=admission.year_level,
            year=admission.school_year
        )

        return admission

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # --- Student Info ---
        student = instance.student
        student_user = student.user
        representation.update({
            "student_first_name": student_user.first_name,
            "student_middle_name": student_user.middle_name,
            "student_last_name": student_user.last_name,
            "student_email": student_user.email,
            "student_date_of_birth": student.date_of_birth,
            "student_gender": student.gender,
            "student_enrolment_date": student.enrolment_date,
            "student_classes": [cls.name for cls in student.classes.all()],
        })

        # --- Guardian Info ---
        guardian = instance.guardian
        guardian_user = guardian.user
        representation.update({
            "guardian_first_name": guardian_user.first_name,
            "guardian_middle_name": guardian_user.middle_name,
            "guardian_last_name": guardian_user.last_name,
            "guardian_email": guardian_user.email,
            "guardian_phone_no": guardian.phone_no,
        })

        # --- Replace FK with readable names ---
        representation["year_level"] = instance.year_level.level_name if instance.year_level else None
        representation["school_year"] = instance.school_year.year_name if instance.school_year else None

        # --- Clean up nested input ---
        representation.pop("student", None)
        representation.pop("guardian", None)

        return representation

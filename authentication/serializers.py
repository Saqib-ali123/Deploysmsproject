from rest_framework.exceptions import ValidationError
from rest_framework import serializers

from authentication.models import User
from director.models import Director, OfficeStaff, Role,YearLevel, SchoolYear, ClassPeriod, Director, Guardian
from director.serializers import RoleSerializer
from student.models import Guardian, Student, StudentYearLevel
from teacher.models import Teacher
# from director.models import 
from django.contrib.auth.password_validation import validate_password


# class UserSerializer(serializers.ModelSerializer):
#     role = serializers.PrimaryKeyRelatedField(
#         queryset=Role.objects.all(), many=True, write_only=True
#     )

#     roles = RoleSerializer(source="role", read_only=True, many=True)

#     class Meta:
#         model = User
#         fields = [
#             "id",
#             "first_name",
#             "last_name",
#             "email",
#             "password",
#             "role",
#             "roles",
#         ]
#         extra_kwargs = {"password": {"write_only": True}}

# class UserSerializer(serializers.ModelSerializer):
#     role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), write_only=True)

#     class Meta:
#         model = User
#         fields = ["first_name", "last_name", "email", "password", "role"]
#         extra_kwargs = {'password': {'write_only': True}}

#     def validate(self, attrs):
#         role = attrs.get('role')
#         if not role:
#             raise ValidationError({"role": "This field is required."})
#         return attrs

#     def create(self, validated_data):
#         role = validated_data.pop("role")  # Get role and remove from validated_data

#         # Create the user
#         user = User.objects.create_user(
#             first_name=validated_data["first_name"],
#             last_name=validated_data["last_name"],
#             email=validated_data["email"],
#             password=validated_data["password"],
#         )

#         # Set the many-to-many role relationship
#         user.role.set([role])

#         # Create related object based on role
#         role_name = role.name.lower()

#         if role_name == "director":
#             Director.objects.create(user=user)
#         elif role_name == "student":
#             Student.objects.create(user=user)
#         elif role_name == "teacher":
#             Teacher.objects.create(user=user)
#         elif role_name == "guardian":
#             Guardian.objects.create(user=user)

#         return user



# class UserSerializer(serializers.ModelSerializer):
#     role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), write_only=True)
#     year_level = serializers.PrimaryKeyRelatedField(queryset=YearLevel.objects.all(), write_only=True, required=False)
#     school_year = serializers.PrimaryKeyRelatedField(queryset=SchoolYear.objects.all(), write_only=True, required=False)
#     gender = serializers.CharField(write_only=True, required=False)
#     date_of_birth = serializers.DateField(write_only=True, required=False)
#     enrolment_date = serializers.DateField(write_only=True, required=False)

#     class Meta:
#         model = User
#         fields = [
#             "first_name", "last_name", "email", "password", "role",
#             "year_level", "school_year", "gender", "date_of_birth", "enrolment_date"
#         ]
#         extra_kwargs = {
#             'password': {'write_only': True},
#         }

#     def validate(self, attrs):
#         validate_password(attrs["password"])

#         role = attrs.get("role")
#         if not role:
#             raise ValidationError({"role": "This field is required."})

#         role_name = role.name.lower()

#         request = self.context.get("request", None)
#         if request is None or not hasattr(request, "user"):
#             raise ValidationError({"error": "Request context is missing or invalid."})

#         user = request.user
#         if not user.is_authenticated:
#             raise ValidationError({"error": "Authentication required to create users."})

#         user_roles = user.role.all()
#         user_role = user_roles[0].name.lower() if user_roles else None

#         if user_role not in [ "director", "office staff"]:
#             raise ValidationError({"error": "You are not allowed to create users."})

#         if user_role == "office staff" and role_name not in ["student", "guardian"]:
#             raise ValidationError({"error": "Office staff can only register students and guardians."})

#         if role_name == "student":
#             required_fields = ["year_level", "school_year", "gender", "date_of_birth", "enrolment_date"]
#             missing_fields = [field for field in required_fields if not attrs.get(field)]
#             if missing_fields:
#                 raise ValidationError({field: "This field is required for students." for field in missing_fields})

#         return attrs


#     def create(self, validated_data):
#         role = validated_data.pop("role")
#         year_level = validated_data.pop("year_level", None)
#         school_year = validated_data.pop("school_year", None)
#         gender = validated_data.pop("gender", None)
#         date_of_birth = validated_data.pop("date_of_birth", None)
#         enrolment_date = validated_data.pop("enrolment_date", None)

#         # Create user
#         user = User.objects.create_user(
#             first_name=validated_data["first_name"],
#             last_name=validated_data["last_name"],
#             email=validated_data["email"],
#             password=validated_data["password"],
#         )
#         user.role.set([role])

#         role_name = role.name.lower()
#         student = None

#         # Create role-specific profile
#         if role_name == "student":
#             student = Student.objects.create(
#                 user=user,
#                 gender=gender,
#                 date_of_birth=date_of_birth,
#                 enrolment_date=enrolment_date
#             )
#         elif role_name == "teacher":
#             Teacher.objects.create(user=user)
#         elif role_name == "director":
#             Director.objects.create(user=user)
#         elif role_name == "guardian":
#             Guardian.objects.create(user=user)
#         elif role_name == "office staff":
#             OfficeStaff.objects.create(user=user)

#         # Link student to year level
#         if student:
#             StudentYearLevel.objects.create(
#                 student=student,
#                 level=year_level,
#                 year=school_year
#             )

#         return user

# ********************user profile*************

class UserSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), write_only=True)
    year_level = serializers.PrimaryKeyRelatedField(queryset=YearLevel.objects.all(), write_only=True, required=False)
    school_year = serializers.PrimaryKeyRelatedField(queryset=SchoolYear.objects.all(), write_only=True, required=False)
    gender = serializers.CharField(write_only=True, required=False)
    date_of_birth = serializers.DateField(write_only=True, required=False)
    enrolment_date = serializers.DateField(write_only=True, required=False)
    user_profile = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email", "password", "role",
            "year_level", "school_year", "gender", "date_of_birth",
            "enrolment_date", "user_profile"
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        validate_password(attrs["password"])

        role = attrs.get("role")
        if not role:
            raise ValidationError({"role": "This field is required."})

        role_name = role.name.lower()

        request = self.context.get("request", None)
        if request is None or not hasattr(request, "user"):
            raise ValidationError({"error": "Request context is missing or invalid."})

        user = request.user
        if not user.is_authenticated:
             raise ValidationError({"error": "Authentication required to create users."})

        user_roles = user.role.all()
        user_role = user_roles[0].name.lower() if user_roles else None

        if user_role not in ["director", "office staff"]:
            raise ValidationError({"error": "You are not allowed to create users."})

        if user_role == "office staff" and role_name not in ["student", "guardian"]:
            raise ValidationError({"error": "Office staff can only register students and guardians."})

        if role_name == "student":
            required_fields = ["year_level", "school_year", "gender", "date_of_birth", "enrolment_date"]
            missing_fields = [field for field in required_fields if not attrs.get(field)]
            if missing_fields:
                raise ValidationError({field: "This field is required for students." for field in missing_fields})

        return attrs

    def create(self, validated_data):
        role = validated_data.pop("role")
        year_level = validated_data.pop("year_level", None)
        school_year = validated_data.pop("school_year", None)
        gender = validated_data.pop("gender", None)
        date_of_birth = validated_data.pop("date_of_birth", None)
        enrolment_date = validated_data.pop("enrolment_date", None)
        user_profile = validated_data.pop("user_profile", None)

        user = User.objects.create_user(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        if user_profile:
            user.user_profile = user_profile
            user.save()

        user.role.set([role])

        role_name = role.name.lower()
        student = None

        if role_name == "student":
            student = Student.objects.create(
                user=user,
                gender=gender,
                date_of_birth=date_of_birth,
                enrolment_date=enrolment_date
            )
        elif role_name == "teacher":
            Teacher.objects.create(user=user)
        elif role_name == "director":
            Director.objects.create(user=user)
        elif role_name == "guardian":
            Guardian.objects.create(user=user)
        elif role_name == "office staff":
            OfficeStaff.objects.create(user=user)

        if student:
            StudentYearLevel.objects.create(
                student=student,
                level=year_level,
                year=school_year
            )

        return user






class ChangePasswordSerializer(serializers.Serializer):
    current_password=serializers.CharField(min_length=8)
    change_password = serializers.CharField(min_length=8)
    email=serializers.EmailField()

# Changes as of 25April25 at 01:00 PM
class LoginSerializers(serializers.Serializer):
    email=serializers.EmailField()
    password=serializers.CharField(max_length=12)
    # role=serializers.CharField(max_length=30)
    

class LogoutSerializers(serializers.Serializer):
    refresh_token=serializers.CharField()


class OtpSerializers(serializers.Serializer):
    email=serializers.EmailField()


class ForgotSerializers(serializers.Serializer):
    email=serializers.EmailField()
    otp=serializers.CharField(max_length=6)
    new_password=serializers.CharField(min_length=8,write_only=True)
    confirm_password=serializers.CharField(min_length=8, write_only=True)

    def validate(self, data):
        if data ['new_password'] != data['confirm_password']:
            raise serializers.ValidationError('Passswrod dont match')
        return data


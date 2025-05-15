from rest_framework import serializers

from authentication.models import User
from director.models import Role, ClassPeriod
from .models import GuardianType, Student, StudentGuardian


from django.db import IntegrityError
from django.core.exceptions import MultipleObjectsReturned

from .models import Guardian
from director.models import BankingDetail


class GuardianTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardianType
        fields = "__all__"


class StudentSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=100, write_only=True)
    middle_name = serializers.CharField(max_length=100, write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100, write_only=True)
    password = serializers.CharField(max_length=100, write_only=True,required=False)
    email = serializers.EmailField(write_only=True)
    classes = serializers.PrimaryKeyRelatedField(
        queryset=ClassPeriod.objects.all(), many=True, required=False, allow_null=True
    )

    def create(self, validated_data):
        user_data = {
            "first_name": validated_data.pop("first_name"),
            "middle_name": validated_data.pop("middle_name", None),
            "last_name": validated_data.pop("last_name"),
            "password": validated_data.pop("password",None),
            "email": validated_data.pop("email"),
        }
        classes_data = validated_data.pop("classes", [])

        try:
            role, created = Role.objects.get_or_create(name="student")
        except MultipleObjectsReturned:
            raise serializers.ValidationError("Something went wrong")

        user = User.objects.filter(email=user_data["email"]).first()

        if user:
            if not user.role.filter(name="student").exists():
                user.role.add(role)
                user.save()
            else:
                raise serializers.ValidationError(
                    "User with this email already exists and is a student."
                )

        else:
            user = User.objects.create_user(**user_data)
            user.role.add(role)
            user.save()

        student = Student.objects.create(user=user, **validated_data)
        student.classes.set(classes_data)
        return student

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        email = user_data.get("email")

        try:
            if email:
                user_instance = User.objects.get(email=email)
                instance.user.email = email
            instance.user.first_name = validated_data.get(
                "first_name", instance.user.first_name
            )
            instance.user.middle_name = validated_data.get(
                "middle_name", instance.user.middle_name
            )
            instance.user.last_name = validated_data.get(
                "last_name", instance.user.last_name
            )

            instance.user.set_password(validated_data.get("password"))
            instance.user.email = validated_data.get("email", instance.user.email)
            instance.date_of_birth = validated_data.get(
                "date_of_birth", instance.date_of_birth
            )
            instance.gender = validated_data.get("gender", instance.gender)
            instance.enrolment_date = validated_data.get(
                "enrolment_date", instance.enrolment_date
            )

            instance.user.save()
            instance.save()

            return instance
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User with provided email does not exist."
            )
        except IntegrityError:
            raise serializers.ValidationError(
                "User data could not be updated.Student email already exists in student table."
            )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update(
            {
                "first_name": instance.user.first_name,
                "middle_name": instance.user.middle_name,
                "last_name": instance.user.last_name,
                "email": instance.user.email,
                "classes": [class_period.id for class_period in instance.classes.all()],
                "date_of_birth": instance.date_of_birth,
                "gender": instance.gender,
                "enrolment_date": instance.enrolment_date,
            }
        )
        return representation

    class Meta:
        model = Student
        exclude = ["user"]
    #     extra_kwargs = {
    # 'password': {'write_only': True},
# }


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name"]


class StudentListSerilaizer(serializers.Serializer):
    email = serializers.EmailField()
    guardian_type = serializers.CharField(max_length=100)


class GuardianSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True, max_length=255)
    middle_name = serializers.CharField(
        write_only=True, max_length=255, allow_blank=True
    )
    last_name = serializers.CharField(write_only=True, max_length=255)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True,required=False)
    students = StudentListSerilaizer(many=True, required=False)

    class Meta:
        model = Guardian
        exclude = ["user"]

    def create(self, validated_data):

        user_data = {
            "first_name": validated_data.pop("first_name", ""),
            "middle_name": validated_data.pop("middle_name", ""),
            "last_name": validated_data.pop("last_name", ""),
            "email": validated_data.pop("email", ""),
            "password": validated_data.pop("password", ""),
        }

        guardian_data = {"phone_no": validated_data.pop("phone_no", "")}
        students_data = validated_data.pop("students", [])

        try:
            role_guardian, _ = Role.objects.get_or_create(name="guardian")

        except MultipleObjectsReturned:
            raise serializers.ValidationError("somthing went wrong!")

        user_instance = User.objects.filter(email=user_data["email"]).first()

        if user_instance:

            if user_instance.role.filter(name="guardian").exists():

                raise serializers.ValidationError(
                    {"message": "User with this email already exists as a guardian."}
                )

            else:

                user_instance.role.add(role_guardian)
                guardian_profile = Guardian.objects.create(
                    user=user_instance, **guardian_data
                )
                return guardian_profile
        else:

            user_instance = User.objects.create_user(**user_data)

            user_instance.role.add(role_guardian)
            guardian_profile = Guardian.objects.create(
                user=user_instance, **guardian_data
            )

            for student_data in students_data:
                guardian_type_name = student_data.get("guardian_type")
                student_email = student_data.get("email")

                try:
                    student = Student.objects.get(user__email=student_email)

                except Student.DoesNotExist:
                    raise serializers.ValidationError(
                        {"message": f"student with '{student_email}' does not exist"}
                    )

                try:
                    guardian_type, _ = GuardianType.objects.get_or_create(
                        name=guardian_type_name
                    )

                except Exception as e:
                    raise serializers.ValidationError(
                        {"message": f"Can't create GuardianType: {str(e)}"}
                    )

                try:
                    StudentGuardian.objects.create(
                        student=student,
                        guardian_type=guardian_type,
                        guardian=guardian_profile,
                    )

                except Exception as e:
                    raise serializers.ValidationError(
                        {"message": f"Can't Establish Relation: {str(e)}"}
                    )
            return guardian_profile

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user_data = {
            "first_name": instance.user.first_name,
            "middle_name": instance.user.middle_name,
            "last_name": instance.user.last_name,
            "email": instance.user.email,
            "phone_no": representation.pop("phone_no", ""),
            # "students": [],
        }
        related_student_gaurdian = instance.studentguardian_set.all()
        for student_gaurdian in related_student_gaurdian:
            student_data = {
                "email": student_gaurdian.student.user.email,
                "guardian_type": student_gaurdian.guardian_type.name,
            }
            user_data["students"].append(student_data)

        return user_data

    def update(self, instance, validated_data):
        instance.phone_no = validated_data.get("phone_no", instance.phone_no)
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

        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"Message": "User doesn't exist with this email!"}
            )

        except IntegrityError:
            raise serializers.ValidationError(
                {"Integrity Error": " Unable to update Data"}
            )

        except Exception:
            raise serializers.ValidationError({"Message": "Somthing went wrong"})
        return instance



# Fee Submission Serializer as of 07May25 at 12:34 PM

class FeeSubmissionSerializer(serializers.Serializer):
    account_no = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=['cash', 'online', 'cheque'])

    def validate_account_no(self, value):
        if not BankingDetail.objects.filter(account_no=value).exists():
            raise serializers.ValidationError("Invalid account number.")
        return value

# json for fee
# {
#   "account_no": 123456789012,
#   "amount": "2000.00",
#   "payment_method": "online"
# }

    
    class Meta:
        model = Guardian
        exclude = ["user"]
    #     extra_kwargs = {
    # 'password': {'write_only': True},
        # }    
        
        
        
        

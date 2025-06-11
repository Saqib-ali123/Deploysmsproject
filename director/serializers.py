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
        
        
class ClassPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassPeriod
        fields = "__all__"        


class BankingDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankingDetail
        fields = ["account_no", "ifsc_code", "holder_name"]
        extra_kwargs = {
            "user": {"read_only": True}  # exclude user from POST input
        }

    def create(self, validated_data):
        # user must be passed manually via serializer context or from parent
        user = self.context.get("user")  # get user from context
        if not user:
            raise serializers.ValidationError("User is required to create banking detail.")

        return BankingDetail.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        instance.account_no = validated_data.get("account_no", instance.account_no)
        instance.ifsc_code = validated_data.get("ifsc_code", instance.ifsc_code)
        instance.holder_name = validated_data.get("holder_name", instance.holder_name)
        instance.save()
        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep.update({
            "first_name": instance.user.first_name,
            "middle_name": instance.user.middle_name,
            "last_name": instance.user.last_name,
            # "email": instance.user.email,  # 
        })
        return rep

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
        
        


class subjectSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'subject_name', 'department'] 

    def get_department(self, obj):
        return obj.department.department_name if obj.department else None



class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = "__all__"


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"




class AddressSerializer(serializers.ModelSerializer):
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())
    state = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())

    country_name = serializers.CharField(source='country.name', read_only=True)
    state_name = serializers.CharField(source='state.name', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)

    class Meta:
        model = Address
        fields = [
            'id', 'user', 'house_no', 'habitation', 'word_no', 'zone_no', 'block', 'district', 'division', 'area_code',
            'country', 'state', 'city', 'address_line',
            'country_name', 'state_name', 'city_name'
        ]
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def validate(self, data):
        # user = data.get('user')  # No need to get user here, it's read-only
        house_no = data.get('house_no')
        area_code = data.get('area_code')
        country = data.get('country')
        state = data.get('state')
        city = data.get('city')
        address_line = data.get('address_line')

        # Access the user from the serializer context
        user = self.context.get('user')

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

        return data



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
    password = serializers.CharField(write_only=True,required=False, allow_null=True)
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
            "password": validated_data.pop("password",""),
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





# ***************guardin type *****************
class AdmissionSerializer(serializers.ModelSerializer):
    student = StudentSerializer(write_only=True)
    guardian = GuardianSerializer(write_only=True)
    guardian_type = serializers.PrimaryKeyRelatedField(
        queryset=GuardianType.objects.all(), write_only=True
    )

    student_data = serializers.SerializerMethodField()

    class Meta:
        model = Admission
        fields = [
            'id', 'student', 'guardian', 'guardian_type', 'student_data',
            'admission_date', 'previous_school_name', 'previous_standard_studied',
            'tc_letter', 'year_level', 'school_year',
            'emergency_contact_n0', 'entire_road_distance_from_home_to_school',
            'obtain_marks', 'total_marks', 'previous_percentage'
        ]
        read_only_fields = ['admission_date']

    def get_student_data(self, obj):
        return StudentSerializer(obj.student).data

    def create(self, validated_data):
        student_data = validated_data.pop("student")
        guardian_data = validated_data.pop("guardian")
        guardian_type = validated_data.pop("guardian_type", '')

        # --- Student creation ---
        student_email = student_data.get("email")
        if Student.objects.filter(user__email__iexact=student_email).exists():
            raise serializers.ValidationError({"student_email": "A student with this email already exists."})

        classes_data = student_data.pop("classes", [])

        user_data = {
            'first_name': student_data.pop('first_name', ''),
            'middle_name': student_data.pop('middle_name', ''),
            'last_name': student_data.pop('last_name', ''),
            'email': student_data.pop('email'),
            'password': student_data.pop('password', None),
            'user_profile': student_data.pop('user_profile', None),
        }

        if User.objects.filter(email=user_data['email']).exists():
            raise serializers.ValidationError("User with this email already exists.")

        role, _ = Role.objects.get_or_create(name='student')
        user = User.objects.create_user(**user_data)
        user.role.add(role)

        # Address data
        address_data = {
            'house_no': student_data.pop('house_no', None),
            'habitation': student_data.pop('habitation', None),
            'word_no': student_data.pop('word_no', None),
            'zone_no': student_data.pop('zone_no', None),
            'block': student_data.pop('block', None),
            'district': student_data.pop('district', None),
            'division': student_data.pop('division', None),
            'area_code': student_data.pop('area_code', None),
            'address_line': student_data.pop('address_line', None),
            'country': student_data.pop('country', None),
            'state': student_data.pop('state', None),
            'city': student_data.pop('city', None),
        }
        address_data = {k: v for k, v in address_data.items() if v is not None}

        # Banking data
        banking_data = {
            'account_no': student_data.pop('account_no', None),
            'ifsc_code': student_data.pop('ifsc_code', None),
            'holder_name': student_data.pop('holder_name', None),
        }
        banking_data = {k: v for k, v in banking_data.items() if v is not None}

        student_data.pop('address', None)
        student_data.pop('banking_detail', None)

        # Create student
        student = Student.objects.create(user=user, **student_data)
        student.classes.set(classes_data)

        if address_data:
            address_data['user'] = user
            Address.objects.create(**address_data)

        if banking_data:
            banking_serializer = BankingDetailsSerializer(data=banking_data, context={'user': user})
            banking_serializer.is_valid(raise_exception=True)
            banking_serializer.save()

        # --- Guardian creation ---
        guardian_email = guardian_data.get("email")
        guardian = Guardian.objects.filter(user__email__iexact=guardian_email).first()
        if not guardian:
            guardian_serializer = GuardianSerializer(data=guardian_data)
            guardian_serializer.is_valid(raise_exception=True)
            guardian = guardian_serializer.save()

        # --- Admission ---
        admission_data = {
            'student': student,
            'guardian': guardian,
            'previous_school_name': validated_data.get('previous_school_name'),
            'previous_standard_studied': validated_data.get('previous_standard_studied'),
            'tc_letter': validated_data.get('tc_letter'),
            'year_level': validated_data.get('year_level'),
            'school_year': validated_data.get('school_year'),
            'emergency_contact_n0': validated_data.get('emergency_contact_n0'),
            'entire_road_distance_from_home_to_school': validated_data.get('entire_road_distance_from_home_to_school'),
            'obtain_marks': validated_data.get('obtain_marks'),
            'total_marks': validated_data.get('total_marks'),
            'previous_percentage': validated_data.get('previous_percentage'),
        }

        admission = Admission.objects.create(**admission_data)

        # --- StudentGuardian ---
        StudentGuardian.objects.get_or_create(
            student=student,
            guardian=guardian,
            guardian_type=guardian_type
        )

        # --- StudentYearLevel ---
        StudentYearLevel.objects.get_or_create(
            student=student,
            level=admission.year_level,
            year=admission.school_year
        )

        return admission

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        student_data = StudentSerializer(instance.student).data
        rep["student_data"] = student_data
        rep["guardian"] = GuardianSerializer(instance.guardian).data

        student_guardian = StudentGuardian.objects.filter(
            student=instance.student,
            guardian=instance.guardian
        ).first()

        rep["guardian_type"] = student_guardian.guardian_type.name if student_guardian else None
        rep["year_level"] = instance.year_level.level_name if instance.year_level else None
        rep["school_year"] = instance.school_year.year_name if instance.school_year else None
        rep['banking_detail'] = student_data.get('banking_detail')

        return rep



# **********Assignment ClassPeriod for Student behalf of YearLevel(Standard)********************

# As of 05May25 at 01:00 PM


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


# 


        
        
        
    

# As of 08may25 at 11:41 AM
class FeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeType
        fields = ['id', 'name', 'description']
        
        
# commented as of 17May25 at 02:00 PM
# class FeeStructureSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FeeStructure
#         fields = ['id', 'year_level', 'term', 'fee_type','total_fee']

# Added this as of 17May25 at 02:00 PM to fetch names instead of ids
class FeeStructureSerializer(serializers.ModelSerializer):
    year_level = serializers.CharField(source='year_level.level_name')
    term = serializers.CharField(source='term.term_number')
    fee_type = serializers.CharField(source='fee_type.name')

    class Meta:
        model = FeeStructure
        fields = ['id', 'year_level', 'term', 'fee_type', 'total_fee']

        
# commented as of 17May25 at 02:00 PM
# class FeeSubmitSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Fee
#         fields = [
#             'id', 'student', 'fee_structure', 'fee_type',
#             'amount_paid', 'payment_mode', 'remarks','receipt_number'
#         ]

# Added this as of 17May25 at 02:00 PM to fetch names instead of ids
class FeeSubmitSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    fee_structure = serializers.SerializerMethodField()
    fee_type = serializers.CharField(source='fee_type.name')

    class Meta:
        model = Fee
        fields = [
            'id', 'student', 'fee_structure', 'fee_type',
            'amount_paid', 'payment_mode', 'remarks', 'receipt_number'
        ]
        
    def get_student(self, obj):
        return str(obj.student)


    def get_fee_structure(self, obj):     # commented as of 28May25 at 02:00 PM
        if obj.fee_structure:
            # return f"{obj.fee_structure.year_level.level_name} - {obj.fee_structure.term.term_number}"
            return f"{obj.fee_structure.year_level.level_name}"
        return None

    # def to_representation(self, instance):     # commented as of 28May25 at 02:00 PM
    #     representation = super().to_representation(instance)

    #     # --- Student Info ---
    #     student = instance.student
    #     student_user = student.user
    #     representation.update({
    #         "student_first_name": student_user.first_name,
    #         "student_middle_name": student_user.middle_name,
    #         "student_last_name": student_user.last_name,
    #         "student_email": student_user.email,
    #         "student_date_of_birth": student.date_of_birth,
    #         "student_gender": student.gender,
    #         "student_enrolment_date": student.enrolment_date,
    #         "student_classes": [cls.name for cls in student.classes.all()],
    #     })

    #     # --- Guardian Info ---    # commented as of 28May25 at 02:00 PM
    #     guardian = instance.guardian
    #     guardian_user = guardian.user
    #     representation.update({
    #         "guardian_first_name": guardian_user.first_name,
    #         "guardian_middle_name": guardian_user.middle_name,
    #         "guardian_last_name": guardian_user.last_name,
    #         "guardian_email": guardian_user.email,
    #         "guardian_phone_no": guardian.phone_no,
    #     })

    #     # --- Replace FK with readable names ---       # commented as of 28May25 at 02:00 PM
    #     representation["year_level"] = instance.year_level.level_name if instance.year_level else None
    #     representation["school_year"] = instance.school_year.year_name if instance.school_year else None

    #     # --- Clean up nested input ---        # commented as of 28May25 at 02:00 PM
    #     representation.pop("student", None)
    #     representation.pop("guardian", None)

    #     return representation



class RazorpayPaymentInitiateSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    fee_structure_id = serializers.IntegerField()
    fee_type_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)



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
    
# class DocumentTypeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DocumentType
#         fields = "__all__" 
            
    
# class FileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = File
#         fields = ['id', 'file']


# class DocumentSerializer(serializers.ModelSerializer):
#     files = FileSerializer(many=True, read_only=True)
#     uploaded_files = serializers.ListField(
#         child=serializers.FileField(),
#         write_only=True,
#         required=True,
#         allow_empty=False
#     )

#     document_types = serializers.PrimaryKeyRelatedField(
#         queryset=DocumentType.objects.all(),
#         many=True,
#         required=True,
#         allow_empty=False
#     )

#     class Meta:
#         model = Document
#         fields = [
#             'id', 'document_types', 'files', 'uploaded_files',
#             'student', 'teacher', 'guardian', 'office_staff', 'uploaded_at'
#         ]

#     def create(self, validated_data):
#         uploaded_files = validated_data.pop('uploaded_files')
#         document_types = validated_data.pop('document_types')

#         # Create Document first
#         document = Document.objects.create(**validated_data)
#         document.document_types.set(document_types)

#         for uploaded_file in uploaded_files:
#             file_instance = File(file=uploaded_file, document=document)
#             file_instance.save()  # This triggers upload_to() and saves the file
#             document.files.add(file_instance)

#         return document
import json

class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = "__all__"


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'file']


class DocumentSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, read_only=True)

    uploaded_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=True,
        allow_empty=False
    )

    document_types = serializers.PrimaryKeyRelatedField(
        queryset=DocumentType.objects.all(),
        many=True,
        required=True,
        allow_empty=False
    )

    # identities as a list (NOT JSONField, just normal string field storing JSON)
    identities = serializers.ListField(
        child=serializers.CharField(),
        write_only=True
    )

    identities_read = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'document_types', 'identities', 'identities_read', 'files', 'uploaded_files',
            'student', 'teacher', 'guardian', 'office_staff', 'uploaded_at'
        ]

    def get_identities_read(self, obj):
        import json
        try:
            return json.loads(obj.identities) if obj.identities else []
        except:
            return []

    def create(self, validated_data):
        import json

        uploaded_files = validated_data.pop('uploaded_files')
        document_types = validated_data.pop('document_types')
        identities_list = validated_data.pop('identities')

        if len(document_types) != len(identities_list):
            raise serializers.ValidationError("Number of document_types and identities must match.")

        document = Document.objects.create(**validated_data)
        document.document_types.set(document_types)
        document.identities = json.dumps(identities_list)
        document.save()

        for uploaded_file in uploaded_files:
            File.objects.create(file=uploaded_file, document=document)

        return document

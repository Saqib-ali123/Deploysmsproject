from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from collections import OrderedDict
from .serializers import *
from rest_framework import status
from rest_framework import viewsets
from rest_framework import filters
from .models import *
from rest_framework .views import APIView       # As of 07May25 at 12:30 PM
# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.db.models import Sum
from rest_framework.decorators import action
from django.db.models.functions import Coalesce
from django.db.models import Sum, DecimalField
# views.py

from django.db.models import Count, F, ExpressionWrapper, IntegerField ,Func , Value

import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404
from datetime import datetime
client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_KEY_SECRET))

import random
import string

# client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_KEY_SECRET))

# client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

### Function to generate auto receipt no. called it inside initiate payment
def generate_receipt_number():
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            if not FeeRecord.objects.filter(receipt_number=code).exists():
                return code


#   ---------------------------------------------  Director Dashboard view   ----------------------------------------------------------


@api_view(["GET"])
def Director_Dashboard_Summary(request):
  
    current_year = datetime.now().year

    summary = {
        "new_admissions": Admission.objects.filter(admission_date__year=current_year).count(),
        "students": Student.objects.count(),
        "teachers": Teacher.objects.count()
    }

    student_total = summary["students"]
    teacher_total = summary["teachers"]

    student_male = Student.objects.filter(gender__iexact="Male").count()
    student_female = Student.objects.filter(gender__iexact="Female").count()

    teacher_male = Teacher.objects.filter(gender__iexact="Male").count()
    teacher_female = Teacher.objects.filter(gender__iexact="Female").count()

    def get_percentage(count, total):
        return round((count / total) * 100, 2) if total else 0

    gender_distribution = {
        "students": {
            "count": {
                "male": student_male,
                "female": student_female
            },
            "percentage": {
                "male": get_percentage(student_male, student_total),
                "female": get_percentage(student_female, student_total)
            },
          
        },
        "teachers": {
            "count": {
                "male": teacher_male,
                "female": teacher_female
            },
            "percentage": {
                "male": get_percentage(teacher_male, teacher_total),
                "female": get_percentage(teacher_female, teacher_total)
            },
            
        }
    }

    class_data = StudentYearLevel.objects.values("level__level_name").annotate(total=Count("student"))
    class_strength = {entry["level__level_name"]: entry["total"] for entry in class_data}


    school_years = SchoolYear.objects.order_by("start_date")
    students_per_year = OrderedDict()

    for year in school_years:
        year_range = f"{year.start_date.year}-{year.end_date.year}"
        count = StudentYearLevel.objects.filter(year=year).count()
        students_per_year[year_range] = count

    return Response({
      
        "summary": summary,
        "gender_distribution": gender_distribution,
        "class_strength": class_strength,
        "students_per_year": students_per_year
    })


# ---------------------------------------------------------   Teacher Dashboard View  ----------------------------------------------------------
 

@api_view(["GET"])
def teacher_dashboard(request, id):
    try:
        user = User.objects.get(id=id)
        teacher = user.teacher
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    except Teacher.DoesNotExist:
        return Response({"error": "This user is not a teacher"}, status=400)

    periods = ClassPeriod.objects.filter(teacher=teacher)
    class_data = []

    for period in periods:
        students = Student.objects.filter(classes=period).distinct()

        # Fetch YearLevel names for these students
        year_levels = YearLevel.objects.filter(
            studentyearlevel__student__in=students
        ).distinct().values_list('level_name', flat=True)

        class_data.append({
            "class_period": period.name,
            "subject": period.subject.subject_name,
            "classroom": period.classroom.room_name,
            "student_count": students.count(),
             "level_name": ", ".join(year_levels) if year_levels else "N/A"
        })

    return Response({
        "teacher": f"{teacher.user.first_name} {teacher.user.last_name}",
        "total_classes": periods.count(),
        "class_details": class_data
    })

#   -------------------------------------------  Guardian Dashboard  ----------------------------------------------------------


@api_view(["GET"])
def guardian_dashboard(request,id=None):
    if not id:
        return Response({"error": "Guardian ID is required"}, status=400)

    try:
        guardian = Guardian.objects.get(id=id)
    except Guardian.DoesNotExist:
        return Response({"error": "Guardian not found"}, status=404)

    student_links = StudentGuardian.objects.filter(guardian=guardian)
    children_data = []

    for link in student_links:
        student = link.student

        # Latest class info (YearLevel + SchoolYear)
        year_level_info = StudentYearLevel.objects.filter(student=student).last()

        children_data.append({
            "student_name": f"{student.user.first_name} {student.user.last_name}",
            "class": f"{year_level_info.level.level_name} ({year_level_info.year.year_name})" if year_level_info else "Not Assigned"
        })

    return Response({
        "guardian": f"{guardian.user.first_name} {guardian.user.last_name}",
        "total_children": student_links.count(),
        "children": children_data
    })

# --------------------------------------------------------- office Staff Dashboard View  ----------------------------------------------------------


@api_view(["GET"])
def office_staff_dashboard(request):
    
    staff = OfficeStaff.objects.first()
    if not staff or not staff.user:
        return Response({"error": "No office staff found"}, status=404)

    
    current_date = datetime.now().date()
    current_year = (
        SchoolYear.objects
        .filter(start_date__lte=current_date, end_date__gte=current_date)
        .order_by('-start_date')
        .first()
    )

    if not current_year:
        return Response({"error": "Current academic year not found"}, status=404)

    new_admissions = Admission.objects.filter(
       admission_date__gte=current_year.start_date,
       admission_date__lte=current_year.end_date
   ).count()

    admission_stats = Admission.objects.values("admission_date__year").annotate(
       total=Count("id")
   ).order_by("admission_date__year")

    trend = OrderedDict()
    for stat in admission_stats:
        year = stat["admission_date__year"]
        trend[str(year)] = stat["total"]

    return Response({
        "staff_name": f"{staff.user.first_name} {staff.user.last_name}",
        "current_academic_year": f"{current_year.start_date.year}-{current_year.end_date.year}",
        "new_admissions_this_year": new_admissions,
        "admissions_per_year": trend
    })





# --------------------------------------------------------- student dashboard View  ----------------------------------------------------------





# @api_view(["GET"])
# def student_dashboard(request, id):
#     try:
#         student = Student.objects.get(id=id)
#     except Student.DoesNotExist:
#         return Response({"error": "Student not found"}, status=404)

#     # Get the latest admission if multiple exist
#     admission = Admission.objects.filter(student=student).order_by('-admission_date').first()
#     if not admission:
#         return Response({"error": "Admission record not found"}, status=404)

#     # Total Fee from YearLevelFee
#     year_level_fees = YearLevelFee.objects.filter(year_level=admission.year_level)
#     total_fee = year_level_fees.aggregate(total=Sum('amount'))['total'] or 0

#     # Paid Amount from FeeRecord
#     paid_amount = FeeRecord.objects.filter(student=student).aggregate(paid=Sum('paid_amount'))['paid'] or 0

#     due_amount = total_fee - paid_amount

#     return Response({
#         "student_name": student.user.get_full_name(),
#         "year_level": str(admission.year_level),
#         "total_fee": float(total_fee),
#         "paid_fee": float(paid_amount),
#         "due_fee": float(due_amount)
#     })


# -------------------------------------------------  Fees summary view  ----------------------------------------------------------







@api_view(["GET"])
def director_fee_summary(request):
    month = request.GET.get("month")  
    year = request.GET.get("year")    

    # School-level summary
    total_students = Student.objects.count()

    fee_qs = FeeRecord.objects.all()

    if month and year:
        fee_qs = fee_qs.filter(month=month, payment_date__year=year)
    elif year:
        fee_qs = fee_qs.filter(payment_date__year=year)

    total_fee = fee_qs.aggregate(
        total=Coalesce(Sum('total_amount', output_field=DecimalField()), Decimal("0.00"))
    )['total']

    total_paid = fee_qs.aggregate(
        paid=Coalesce(Sum('paid_amount', output_field=DecimalField()), Decimal("0.00"))
    )['paid']

    total_due = fee_qs.aggregate(
        due=Coalesce(Sum('due_amount', output_field=DecimalField()), Decimal("0.00"))
    )['due']

    # Class-wise summary
    class_data = []
    all_class_periods = ClassPeriod.objects.select_related('classroom__room_type').all()

    for period in all_class_periods:
        students_in_class = Student.objects.filter(classes=period).distinct()
        student_ids = students_in_class.values_list('id', flat=True)

        class_fee_qs = FeeRecord.objects.filter(student_id__in=student_ids)
        if month and year:
            class_fee_qs = class_fee_qs.filter(month=month, payment_date__year=year)

        class_total_fee = class_fee_qs.aggregate(
            total=Coalesce(Sum('total_amount', output_field=DecimalField()), Decimal("0.00"))
        )['total']

        class_total_paid = class_fee_qs.aggregate(
            paid=Coalesce(Sum('paid_amount', output_field=DecimalField()), Decimal("0.00"))
        )['paid']

        class_total_due = class_fee_qs.aggregate(
            due=Coalesce(Sum('due_amount', output_field=DecimalField()), Decimal("0.00"))
        )['due']

        class_data.append({
            "class_name": f"{period.classroom.room_type} - {period.classroom.room_name}",
            "total_students": students_in_class.count(),
            "total_fee": class_total_fee,
            "paid_fee": class_total_paid,
            "due_fee": class_total_due
        })

    data = {
        "school_summary": {
            "total_students": total_students,
            "total_fee": total_fee,
            "paid_fee": total_paid,
            "due_fee": total_due,
        },
        "class_summary": class_data
    }

    return Response(data)


# -------------------------------------------------  Guardian income distribution view  ----------------------------------------------------------





@api_view(["GET"])
def guardian_income_distribution(request):
    bucket_size = int(request.GET.get("bucket_size", 10000)) 
    max_income = int(request.GET.get("max_income", 200000))   

    income_bucket_expr = ExpressionWrapper(
        Func(
            F('annual_income') / Value(bucket_size),
            function='FLOOR'
        ),
        output_field=IntegerField()
    )

    data = (
        Guardian.objects
        .filter(annual_income__lt=max_income)
        .annotate(income_bucket=income_bucket_expr)
        .values('income_bucket')
        .annotate(count=Count('id'))
        .order_by('income_bucket')
    )

    result = []
    for row in data:
        start = row['income_bucket'] * bucket_size
        end = start + bucket_size
        result.append({
            "range": f"₹{start} - ₹{end}",
            "count": row["count"]
        })

    return Response(result)


# ------------------------------------------------------------------------  livelihood  distribution view  ----------------------------------------------------------


@api_view(["GET"])
def livelihood_distribution(request):
    govt_count = Guardian.objects.filter(means_of_livelihood='Govt').count()
    non_govt_count = Guardian.objects.filter(means_of_livelihood='Non-Govt').count()

    return Response([
        {"category": "Government", "count": govt_count},
        {"category": "Non-Government", "count": non_govt_count}
    ])



# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------







@api_view(["GET", "POST", "PUT", "DELETE"])
def YearLevelView(request, id=None):
    if request.method == "GET":
        if id is not None:
            try:
                YearLevels = YearLevel.objects.get(pk=id)
                serialize = YearLevelSerializer(YearLevels, many=False)
                return Response(serialize.data, status=status.HTTP_200_OK)
            except YearLevel.DoesNotExist:
                return Response(
                    data={"message": "Data Not Found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception as e:
                return Response(
                    data={"message": f"something went wrong {e}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            YearLevels = YearLevel.objects.all()
            serialized = YearLevelSerializer(YearLevels, many=True)
            return Response(serialized.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        data = request.data
        serialize = YearLevelSerializer(data=data)
        if serialize.is_valid():
            serialize.save()
            return Response(
                {"message": "Data Saved Successfully"}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"message": "Insert Valid Data"}, status=status.HTTP_400_BAD_REQUEST
        )

    elif request.method == "PUT":
        if id is None:
            return Response(
                {"message": "Id is Required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = YearLevel.objects.get(pk=id)
            serialize = YearLevelSerializer(
                instance=data, data=request.data, partial=True
            )
            if serialize.is_valid():
                serialize.save()
                return Response(
                    {"message": "Data Updated Successfully"},
                    status=status.HTTP_202_ACCEPTED,
                )
            return Response(
                {"message": "Insert Valid Data"}, status=status.HTTP_400_BAD_REQUEST
            )
        except YearLevel.DoesNotExist:
            return Response(
                {"message": "Data Not Found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": "something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    elif request.method == "DELETE":
        if id is None:
            return Response(
                {"message": "Id is Required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = YearLevel.objects.get(pk=id)
            data.delete()
            return Response(
                {"message": "Data Deleted Successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except YearLevel.DoesNotExist:
            return Response(
                {"message": "Data Not Found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": "something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["GET", "POST", "PUT", "DELETE"])
def SchoolYearView(request, pk=None):

    if request.method == "GET":
        if pk is not None:
            try:
                store = SchoolYear.objects.get(id=pk)
                serialize_rData = SchoolYearSerializer(store, many=False)
                return Response(serialize_rData.data, status=status.HTTP_200_OK)

            except SchoolYear.DoesNotExist:
                return Response(
                    {"Message": "Data Not Found"}, status=status.HTTP_404_NOT_FOUND
                )

        else:
            store = SchoolYear.objects.all()
            print("\n\n", store, "\n\n")
            serializerData = SchoolYearSerializer(store, many=True)
            return Response(serializerData.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        json_data = request.data
        serializerData = SchoolYearSerializer(data=json_data)

        if serializerData.is_valid():
            serializerData.save()
            return Response(
                {"Message": "School Year Added Successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response({"Message": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        try:
            Store = SchoolYear.objects.get(id=pk)
            Updated_SchoolYear = SchoolYearSerializer(instance=Store, data=request.data)

            if Updated_SchoolYear.is_valid():
                Updated_SchoolYear.save()
                return Response(
                    {"message": "Update School Year Successfully"},
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {"message": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST
            )

        except SchoolYear.DoesNotExist:
            return Response(
                {"Message": "Data Not Found"}, status=status.HTTP_404_NOT_FOUND
            )

    elif request.method == "DELETE":
        try:
            store = SchoolYear.objects.get(id=pk)
            store.delete()
            return Response(
                {"Message": "School year Delete Successfuly"},
                status=status.HTTP_204_NO_CONTENT,
            )

        except SchoolYear.DoesNotExist:
            return Response(
                {"Message": "Data Not Found"}, status=status.HTTP_404_NOT_FOUND
            )


@api_view(["GET", "POST", "PUT", "DELETE"])
def DepartmentView(request, pk=None):
    if request.method == "GET":
        if pk is not None:
            try:
                department = Department.objects.get(id=pk)
                serializer = DepartmentSerializer(department, many=False)
                return Response(serializer.data, status=status.HTTP_200_OK)

            except Department.DoesNotExist:
                return Response(
                    {"Message": "Data Not Found"}, status=status.HTTP_404_NOT_FOUND
                )

            except Exception as e:
                return Response(
                    {"Message": "Something went wrong"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        else:
            departments = Department.objects.all()
            serializer = DepartmentSerializer(departments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        json_data = request.data

        if json_data.get("department_name", None) is None:
            return Response(
                {"Message": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST
            )

        json_data["department_name"] = json_data["department_name"].lower()

        serializer = DepartmentSerializer(data=json_data)

        if serializer.is_valid():

            if Department.objects.filter(
                department_name=json_data["department_name"]
            ).exists():
                return Response(
                    {"Message": "Department Already Exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save()
            return Response(
                {"Message": "Department Added Successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response({"Message": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":

        if request.data.get("department_name", None) is None:
            return Response(
                {"Message": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST
            )

        request.data["department_name"] = request.data["department_name"].lower()

        try:
            department = Department.objects.get(id=pk)
            serializer = DepartmentSerializer(instance=department, data=request.data)

            if serializer.is_valid():
                if Department.objects.filter(
                    department_name=request.data["department_name"].lower()
                ).exists():
                    return Response(
                        {"Message": "Department Already Exist"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                serializer.save()

                return Response(
                    {"Message": "Department updated Successfully"},
                    status=status.HTTP_201_CREATED,
                )

        except Department.DoesNotExist:
            return Response(
                {"Message": "Data Not Found"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"Message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    elif request.method == "DELETE":

        try:
            store = Department.objects.get(id=pk)
            store.delete()
            return Response(
                {"Message": "Department Delete Successfuly"},
                status=status.HTTP_204_NO_CONTENT,
            )

        except Department.DoesNotExist:
            return Response(
                {"Message": "Data Not Found"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"Message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["GET", "POST", "PUT", "DELETE"])
def ClassRoomTypeView(request, pk=None):

    if request.method == "GET":
        if pk is not None:
            try:
                classroom_type = ClassRoomType.objects.get(id=pk)
                serialize = ClassRoomTypeSerializer(classroom_type, many=False)
                return Response(serialize.data, status.HTTP_200_OK)

            except ClassRoomType.DoesNotExist:
                return Response(
                    {"Message": "Data not found"}, status.HTTP_404_NOT_FOUND
                )
        else:
            classroom_types = ClassRoomType.objects.all()
            serialized = ClassRoomTypeSerializer(classroom_types, many=True)
            return Response(serialized.data, status.HTTP_200_OK)

    elif request.method == "POST":
        data = request.data
        data["name"] = data["name"].lower()
        serialize = ClassRoomTypeSerializer(data=data)
        if serialize.is_valid():

            if ClassRoomType.objects.filter(name=data["name"]).exists():

                return Response(
                    {"Message": "Classroom Type Already Exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serialize.save()
            return Response({"Message": "Data Saved Successfully"}, status.HTTP_200_OK)
        return Response({"Message": "Insert Valid Data"}, status.HTTP_201_CREATED)

    elif request.method == "PUT":
        try:
            data = ClassRoomType.objects.get(id=pk)

            if request.data.get("name", None) is None:
                return Response(
                    {"Message": "Invalid Data"}, status.HTTP_400_BAD_REQUEST
                )

            request.data["name"] = request.data["name"].lower()

            serialize = ClassRoomTypeSerializer(instance=data, data=request.data)
            if serialize.is_valid():

                if ClassRoomType.objects.filter(
                    name=request.data["name"].lower()
                ).exists():
                    return Response(
                        {"Message": "Classroom Type Already Exist"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                serialize.save()
                return Response(
                    {"Message": "Data Updated Successfully"}, status.HTTP_200_OK
                )
            return Response(
                {"Message": "Insert Valid Data"}, status.HTTP_400_BAD_REQUEST
            )

        except ClassRoomType.DoesNotExist:
            return Response({"Message": "Data not found"}, status.HTTP_404_NOT_FOUND)

 
    elif request.method == "DELETE":
        try:
            data = ClassRoomType.objects.get(id=pk)
            data.delete()
            return Response({"Message": "Data Deleted"}, status.HTTP_204_NO_CONTENT)

        except ClassRoomType.DoesNotExist:
            return Response({"Message": "Data not found"}, status.HTTP_404_NOT_FOUND)


# @api_view(["GET", "POST", "PUT", "DELETE"])
# def RoleView(request, pk=None):
#     if request.method == "GET":
#         if pk is not None:
#             try:
#                 role = Role.objects.get(pk=pk)
#                 serialize_Data = RoleSerializer(role, many=False)
#                 return Response(serialize_Data.data, status=status.HTTP_200_OK)

#             except Role.DoesNotExist:
#                 return Response(
#                     {"message": "Role not found"}, status=status.HTTP_404_NOT_FOUND
#                 )

#         else:
#             roles = Role.objects.all()
#             serializerData = RoleSerializer(roles, many=True)
#             return Response(serializerData.data, status=status.HTTP_200_OK)

#     elif request.method == "POST":
#         json_data = request.data

#         # Here we are converting the entered role name to lowercase
#         role = json_data.get("name", "").lower()

#         print(role)
#         json_data["name"] = role

#         # Here we are checking whether entered role already exist or not
#         role = Role.objects.filter(name__iexact=role)

#         if role.exists():
#             return Response(
#                 {"message": "Role already exists"}, status=status.HTTP_400_BAD_REQUEST
#             )

#         serializer = RoleSerializer(data=json_data)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"message": "New Role added Successfully"},
#                 status=status.HTTP_201_CREATED,
#             )

#         return Response({"message": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)

#     elif request.method == "PUT":
#         try:
#             role = Role.objects.get(pk=pk)

#             if request.data.get("name", None) is None:
#                 return Response(
#                     {"message": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST
#                 )

#             request.data["name"] = request.data["name"].lower()

#             updated_Role = RoleSerializer(instance=role, data=request.data)

#             if updated_Role.is_valid():
#                 updated_Role.save()
#                 return Response(
#                     {"message": "Role updated Successfully"},
#                     status=status.HTTP_201_CREATED,
#                 )

#             return Response(
#                 {"message": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST
#             )

#         except Role.DoesNotExist:
#             return Response(
#                 {"message": "Role ID not Found"}, status=status.HTTP_404_NOT_FOUND
#             )

#     elif request.method == "DELETE":
#         try:
#             role = Role.objects.get(pk=pk)
#             role.delete()
#             return Response(
#                 {"message": "Role deleted Successfuly"},
#                 status=status.HTTP_204_NO_CONTENT,
#             )

#         except Role.DoesNotExist:
#             return Response(
#                 {"message": "Role not Found"}, status=status.HTTP_404_NOT_FOUND
#             )

### --- Added this as of 06June25 at 12:00 PM

def get_or_create_role(role_name: str):
    role_name = role_name.strip().lower()
    role, created = Role.objects.get_or_create(
        name__iexact=role_name,
        defaults={"name": role_name}
    )
    return role

@api_view(["GET", "POST", "PUT", "DELETE"])
def RoleView(request, pk=None):
    if request.method == "GET":
        if pk:
            try:
                role = Role.objects.get(pk=pk)
                serializer = RoleSerializer(role)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Role.DoesNotExist:
                return Response({"message": "Role not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            roles = Role.objects.all()
            serializer = RoleSerializer(roles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        role_name = request.data.get("name", "").strip().lower()

        if not role_name:
            return Response({"message": "Role name is required"}, status=status.HTTP_400_BAD_REQUEST)

        existing_role = Role.objects.filter(name__iexact=role_name).first()
        if existing_role:
            return Response({"message": "Role already exists"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RoleSerializer(data={"name": role_name})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "New Role added Successfully"}, status=status.HTTP_201_CREATED)

        return Response({"message": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        if not pk:
            return Response({"message": "Role ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            role = Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return Response({"message": "Role ID not Found"}, status=status.HTTP_404_NOT_FOUND)

        new_name = request.data.get("name", "").strip().lower()

        if not new_name:
            return Response({"message": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)

        if Role.objects.exclude(pk=pk).filter(name__iexact=new_name).exists():
            return Response({"message": "Role with this name already exists"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RoleSerializer(instance=role, data={"name": new_name})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Role updated Successfully"}, status=status.HTTP_200_OK)

        return Response({"message": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        if not pk:
            return Response({"message": "Role ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            role = Role.objects.get(pk=pk)
            role.delete()
            return Response({"message": "Role deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Role.DoesNotExist:
            return Response({"message": "Role not Found"}, status=status.HTTP_404_NOT_FOUND)





# ==============Country================
class CountryView(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    
# ==============Subject================
class subjectView(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = subjectSerializer


# ===============State===================
class StateView(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer


# ================City===============
class CityView(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


# ===========Address==========

# class AddressView(viewsets.ModelViewSet):
#     queryset = Address.objects.all()
#     serializer_class = AddressSerializer


# ===========Period============


class PeriodView(viewsets.ModelViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer


class DirectorView(viewsets.ModelViewSet):
    queryset = Director.objects.all()
    serializer_class = DirectorProfileSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user_instance = instance.user
        if user_instance.role.exclude(name="director").exists():
            try:
                role = Role.objects.get(name="director")
                user_instance.role.remove(role)
            except Role.DoesNotExist:
                pass
            self.perform_destroy(instance)
        else:
            instance.delete()
            user_instance.delete()
        return Response(
            {"success": "Successfully deleted"}, status=status.HTTP_204_NO_CONTENT
        )


# ==============Country================
class CountryView(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


# ===============State===================
class StateView(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer


# ================City===============
class CityView(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


# ===========Address==========
# class AddressView(viewsets.ModelViewSet):
#     queryset = Address.objects.all()
#     serializer_class = AddressSerializer

# Added as of 28April25

class AddressView(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


# ===========Period============


class PeriodView(viewsets.ModelViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer
    
    
class ClassPeriodView(viewsets.ModelViewSet):
    queryset = ClassPeriod.objects.all()
    serializer_class = ClassPeriodSerializer    


class DirectorView(viewsets.ModelViewSet):
    queryset = Director.objects.all()
    serializer_class = DirectorProfileSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user_instance = instance.user
        if user_instance.role.exclude(name="director").exists():
            try:
                role = Role.objects.get(name="director")
                user_instance.role.remove(role)
            except Role.DoesNotExist:
                pass
            self.perform_destroy(instance)
        else:
            instance.delete()
            user_instance.delete()
        return Response(
            {"success": "Successfully deleted"}, status=status.HTTP_204_NO_CONTENT
        )


class BankingDetailView(viewsets.ModelViewSet):
    queryset = BankingDetail.objects.all()
    serializer_class = BankingDetailsSerializer


class DirectorView(viewsets.ModelViewSet):
    queryset = Director.objects.all()
    serializer_class = DirectorProfileSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user_instance = instance.user
        if user_instance.role.exclude(name="director").exists():
            try:
                role = Role.objects.get(name="director")
                user_instance.role.remove(role)
            except Role.DoesNotExist:
                pass
            self.perform_destroy(instance)
        else:
            instance.delete()
            user_instance.delete()
        return Response(
            {"success": "Successfully deleted"}, status=status.HTTP_204_NO_CONTENT
        )


class BankingDetails(viewsets.ModelViewSet):
    queryset = BankingDetail.objects.all()
    serializer_class = BankingDetailsSerializer


class TermView(viewsets.ModelViewSet):
    queryset =Term.objects.all()
    serializer_class = TermSerializer


class AdmissionView(viewsets.ModelViewSet):
    queryset = Admission.objects.all()
    serializer_class = AdmissionSerializer
    
class OfficeStaffView(viewsets.ModelViewSet):
    queryset=OfficeStaff.objects.all()
    serializer_class = OfficeStaffSerializer    
    
#  ***************************   
class DocumentTypeView(viewsets.ModelViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer 
    
class FileView(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer 


# from rest_framework.parsers import MultiPartParser, FormParser

# class DocumentView(viewsets.ModelViewSet):
#     queryset = Document.objects.all()
#     serializer_class = DocumentSerializer
#     parser_classes = (MultiPartParser, FormParser)

#     def create(self, request, *args, **kwargs):
#         print("Request FILES:", request.FILES)
#         print("Request DATA:", request.data)

#         files = request.FILES.getlist('uploaded_files')
#         document_types = request.data.getlist('document_types')

#         if not files:
#             return Response({"error": "No files uploaded"}, status=status.HTTP_400_BAD_REQUEST)
#         if not document_types:
#             return Response({"error": "At least one document type must be selected."}, status=status.HTTP_400_BAD_REQUEST)

#         data = request.data.copy()
#         data.setlist('uploaded_files', files)
#         data.setlist('document_types', document_types)

#         serializer = self.get_serializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import json  # 🔸 This goes at the top of the file

class DocumentView(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        files = request.FILES.getlist('uploaded_files')
        document_types = request.data.getlist('document_types')
        identities = request.data.getlist('identities')

        if not files:
            return Response({"error": "No files uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        if not document_types:
            return Response({"error": "At least one document type must be selected."}, status=status.HTTP_400_BAD_REQUEST)
        if not identities:
            return Response({"error": "Identities are required."}, status=status.HTTP_400_BAD_REQUEST)

        if len(document_types) != len(identities):
            return Response({"error": "Identities count must match document types count."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data.setlist('uploaded_files', files)
        data.setlist('document_types', document_types)
        data.setlist('identities', identities)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)






    # parser_classes = [MultiPartParser, FormParser]  # Important for file uploads

    # def create(self, request, *args, **kwargs):
    #     document_types = request.data.getlist('document_types')
    #     student = request.data.get('student')
    #     teacher = request.data.get('teacher')
    #     guardian = request.data.get('guardian')
    #     office_staff = request.data.get('office_staff')
    #     uploaded_files = request.FILES.getlist('files')

    #     if not uploaded_files:
    #         return Response({"error": "No files uploaded"}, status=status.HTTP_400_BAD_REQUEST)

    #     file_objs = [File.objects.create(file=f) for f in uploaded_files]

    #     document = Document.objects.create(
    #         student_id=student,
    #         teacher_id=teacher,
    #         guardian_id=guardian,
    #         office_staff_id=office_staff
    #     )
    #     document.files.set(file_objs)
    #     document.document_types.set(document_types)
    #     document.save()

    #     serializer = self.get_serializer(document)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    
# **********************************    

    
    
    
# **************Assignment ClassPeriod for Student behalf of YearLevel(standard)****************   
    
# As of 05May25 at 01:00 PM

class ClassPeriodView(viewsets.ModelViewSet):
    queryset = ClassPeriod.objects.all()
    serializer_class = ClassPeriodSerializer
    
    @action(detail=False, methods=["post"], url_path="assign-to-yearlevel")
    def assign_to_yearlevel(self, request):
        serializer = ClassPeriodSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response({
                "message": "ClassPeriods assigned successfully.",
                "details": result
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    
    
# As of 07May25 at 12:30 PM
#commented as of 04June25 at 12:00 AM
# class FeeTypeView(viewsets.ModelViewSet):
#     queryset = FeeType.objects.all()
#     serializer_class = FeeTypeSerializer
    
    
# class FeeStructureView(viewsets.ModelViewSet):
#     queryset = FeeStructure.objects.all()
#     serializer_class = FeeStructureSerializer


# #     # added this code as of 13may25 at 03:45 PM
# class FeeSubmitView(viewsets.ModelViewSet):
#     queryset = Fee.objects.all()
#     serializer_class = FeeSubmitSerializer

#     @action(detail=True, methods=['get'], url_path='summary')
#     def fee_summary(self, request, pk=None):  # `pk` is student_id
#         try:
#             student = Student.objects.get(id=pk)
#         except Student.DoesNotExist:
#             return Response({"error": "Student not found"}, status=404)

#         student_data = {
#             "student_id": student.id,
#             "student_name": student.user.get_full_name(),
#             "fee_details": []
#         }

#         for fee_structure in FeeStructure.objects.all():
#             fee_type = fee_structure.fee_type
#             amount_to_be_paid = float(fee_structure.total_fee)

#             amount_paid = Fee.objects.filter(
#                 student=student,
#                 fee_structure=fee_structure,
#                 fee_type=fee_type
#             ).aggregate(total=Sum('amount_paid'))['total'] or 0.0

#             amount_due = round(amount_to_be_paid - float(amount_paid), 2)

#             latest_payment = Fee.objects.filter(
#                 student=student,
#                 fee_structure=fee_structure,
#                 fee_type=fee_type
#             ).order_by('-payment_date').first()

#             if latest_payment:
#                 payment_date = latest_payment.payment_date.strftime('%Y-%m-%d') 
#                 payment_mode = latest_payment.payment_mode
#                 receipt_number = str(latest_payment.receipt_number) 
#             else:
#                 payment_date = None
#                 payment_mode = None
#                 receipt_number = None

#             student_data["fee_details"].append({
#                 "fee_structure": f"{fee_structure.year_level} - {fee_structure.term}",
#                 "total_fee": amount_to_be_paid,
#                 "fee_type": fee_type.name,
#                 "amount_to_be_paid": amount_to_be_paid,
#                 "amount_paid": float(amount_paid),
#                 "amount_due": amount_due,
#                 "payment_date": payment_date,
#                 "payment_mode": payment_mode,
#                 "receipt_number": receipt_number
#             })

#         return Response(student_data)
    #commented as of 04June25 at 12:00 AM   
    
# As of 04June2025 at 12:15 AM
# Re-implementation of Fee module based on the provided fee card
from django.db.models import Q
from collections import OrderedDict, defaultdict


class FeeTypeView(viewsets.ModelViewSet):
    queryset = FeeType.objects.all()
    serializer_class = FeeTypeSerializer


class YearLevelFeeView(viewsets.ModelViewSet):
    serializer_class = YearLevelFeeSerializer

    def get_queryset(self):
        return YearLevelFee.objects.select_related('year_level', 'fee_type')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        grouped_fees = YearLevelFeeSerializer.group_by_year_level(serializer.data)
        return Response(grouped_fees)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset().filter(year_level__id=pk)
        if not queryset.exists():
            return Response({"detail": "Not found."}, status=404)

        serializer = self.get_serializer(queryset, many=True)
        grouped_fees = YearLevelFeeSerializer.group_by_year_level(serializer.data)
        return Response(grouped_fees[0] if grouped_fees else {})
    
    

class FeeRecordView(viewsets.ModelViewSet):
    serializer_class = FeeRecordSerializer
    queryset = FeeRecord.objects.all()
    filter_backends = [SearchFilter]

    # Enables search using ?search=something
    search_fields = [
        'remarks',
        'receipt_number',
        'student__user__first_name',
        'student__user__last_name',
        'year_level_fees__year_level__level_name',
    ]

    # Optional filtering by year_level using ?year_level=ID
    def get_queryset(self):
        queryset = super().get_queryset()
        request = self.request

        # Filter by year level (optional)
        year_level_id = request.query_params.get('year_level')
        if year_level_id:
            queryset = queryset.filter(year_level_fees__year_level__id=year_level_id)

        # Full name search
        search = request.query_params.get('search')
        if search:
            search = search.strip()
            # Handle "first last" or "just first"
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=search) |
                Q(student__user__last_name__icontains=search) |
                Q(student__user__first_name__icontains=search.split(' ')[0]) &
                Q(student__user__last_name__icontains=' '.join(search.split(' ')[1:]))
            )

        return queryset.distinct()
    
    @action(detail=False, methods=['post'], url_path='submit_single_multi_month_fees')
    def submit_single_multi_month_fees(self, request):
        student_id = request.data.get('student_id')
        months = request.data.get('months', [])
        year_level_fees = request.data.get('year_level_fees', [])
        paid_amount = request.data.get('paid_amount')
        payment_mode = request.data.get('payment_mode')
        remarks = request.data.get('remarks')
        signature = request.data.get('signature')

        if not months or not isinstance(months, list):
            return Response({"error": "Months must be a non-empty list."}, status=status.HTTP_400_BAD_REQUEST)

        responses = []
        for month in months:
            serializer = self.get_serializer(data={
                "student_id": student_id,
                "month": month,
                "year_level_fees": year_level_fees,
                "paid_amount": paid_amount,
                "payment_mode": payment_mode,
                "remarks": f"{remarks or ''} ({month})",
                "signature": signature
            })
            if serializer.is_valid():
                serializer.save()
                responses.append(serializer.data)
            else:
                responses.append({"month": month, "errors": serializer.errors})

        return Response(responses, status=status.HTTP_200_OK)

### Razorpay custom views

    ### using custom view
    @action(detail=False, methods=["post"], url_path="initiate-payment")
    def initiate_payment(self, request):
        serializer = FeeRecordRazorpaySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        validated_data = serializer.validated_data
        total = validated_data['total_amount']
        late_fee = validated_data['late_fee']
        amount = total + late_fee
        
        # Generate unique receipt number
        receipt_number = generate_receipt_number()

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            'amount': int(amount * 100),  # in paise
            'currency': 'INR',
            'payment_capture': '1',
            'receipt': receipt_number
        })

        return Response({
            'razorpay_order_id': razorpay_order['id'],
            # 'razorpay_key': settings.RAZORPAY_KEY_ID,
            'amount': float(amount),
            'currency': 'INR',
            'receipt_number': receipt_number
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="confirm-payment")
    def confirm_payment(self, request):
        data = request.data
        try:
            razorpay_payment_id = data["razorpay_payment_id"]
            razorpay_order_id = data["razorpay_order_id"]
            razorpay_signature_id = data["razorpay_signature_id"]
            student_id = data["student_id"]
            month = data["month"]
            fee_ids = data["year_level_fees"]
        except KeyError:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature_id": razorpay_signature_id
            })
        except razorpay.errors.SignatureVerificationError:
            return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)

        # Create FeeRecord
        student = Student.objects.get(id=student_id)
        year_level_fees = YearLevelFee.objects.filter(id__in=fee_ids)
        total = sum(fee.amount for fee in year_level_fees)
        late_fee = Decimal("25.00") if date.today().day > 15 else Decimal("0.00")
        total_paid = total + late_fee

        fee_record = FeeRecord.objects.create(
            student=student,
            month=month,
            total_amount=total,
            paid_amount=total_paid,
            due_amount=0,
            payment_date=date.today(),
            payment_mode='Online',
            late_fee=late_fee,
            payment_status='Paid',
            remarks='Paid via Razorpay',
            signature='Verified Online',
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature_id=razorpay_signature_id
        )
        fee_record.year_level_fees.set(year_level_fees)

        return Response({
            "message": "Payment successful and FeeRecord saved.",
            "receipt_number": fee_record.receipt_number
        }, status=status.HTTP_201_CREATED)





     
    
    # 🔹 Razorpay Initiate Payment      #commented as of 04June25 at 12:00 AM
    # @action(detail=False, methods=['post'], url_path='initiate-payment')
    # def initiate_payment(self, request):
    #     serializer = RazorpayPaymentInitiateSerializer(data=request.data)
    #     if serializer.is_valid():
    #         data = serializer.validated_data

    #         # Safely fetch the objects, return 404 if not found
    #         student = get_object_or_404(Student, id=data['student_id'])
    #         fee_structure = get_object_or_404(FeeStructure, id=data['fee_structure_id'])
    #         fee_type = get_object_or_404(FeeType, id=data['fee_type_id'])

    #         try:
    #             # Convert amount to paise (minor currency unit)
    #             amount_paise = int(data['amount'] * 100)
    #             receipt_id = f"receipt_{student.id}_{fee_type.id}"

    #             # Create Razorpay order
    #             order = client.order.create({
    #                 "amount": amount_paise,
    #                 "currency": "INR",
    #                 "receipt": receipt_id,
    #                 "payment_capture": 1
    #             })

    #             # Save the fee record
    #             Fee.objects.create(
    #                 student=student,
    #                 fee_structure=fee_structure,
    #                 fee_type=fee_type,
    #                 amount_paid=data['amount'],
    #                 payment_mode='Online',
    #                 razorpay_order_id=order['id']
    #             )

    #             return Response({
    #                 "order_id": order['id'],
    #                 "amount": data['amount'],
    #                 "currency": "INR",
    #                 "student_id": student.id,
    #                 "razorpay_key": settings.RAZORPAY_API_KEY,
    #                 "receipt": receipt_id
    #             })

    #         except Exception as e:
    #             return Response({"error": f"Payment initiation failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # # 🔹 Razorpay Verify Payment
    # @action(detail=False, methods=['post'], url_path='verify-payment')
    # def verify_payment(self, request):
    #     data = request.data
    #     try:
    #         client.utility.verify_payment_signature({
    #             'razorpay_order_id': data['razorpay_order_id'],
    #             'razorpay_payment_id': data['razorpay_payment_id'],
    #             'razorpay_signature': data['razorpay_signature']
    #         })

    #         fee = Fee.objects.get(razorpay_order_id=data['razorpay_order_id'])
    #         fee.razorpay_payment_id = data['razorpay_payment_id']
    #         fee.razorpay_signature = data['razorpay_signature']
    #         fee.save()

    #         return Response({"message": "Payment verified successfully."})
    #     except razorpay.errors.SignatureVerificationError:
    #         return Response({"message": "Payment verification failed."}, status=400)

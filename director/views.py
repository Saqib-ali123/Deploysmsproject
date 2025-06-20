from rest_framework.decorators import api_view
from rest_framework.response import Response

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
import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404
import random
import string
from django.db.models import Sum, F, Value, DecimalField
from django.db.models.functions import Coalesce
from django.db.models import Q
from django.db.models import Q, Sum, Value, FloatField


# client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_KEY_SECRET))
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

### Function to generate auto receipt no. called it inside initiate payment
def generate_receipt_number():
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            if not FeeRecord.objects.filter(receipt_number=code).exists():
                return code



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
    
class DocumentView(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer 
    
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
    
    
# Fee Record View
# https://187gwsw1-8000.inc1.devtunnels.ms/d/fee-record/
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
    
    # https://187gwsw1-8000.inc1.devtunnels.ms/d/fee-record/?year_level=6
    def get_queryset(self):
        queryset = super().get_queryset()
        request = self.request

        year_level_id = request.query_params.get('year_level')
        if year_level_id:
            queryset = queryset.filter(year_level_fees__year_level__id=year_level_id)

        search = request.query_params.get('search')
        if search:
            search = search.strip()
            search_parts = search.split(" ")

            if len(search_parts) > 1:
                queryset = queryset.filter(
                    Q(student__user__first_name__icontains=search_parts[0]) &
                    Q(student__user__last_name__icontains=' '.join(search_parts[1:]))
                )
            else:
                queryset = queryset.filter(
                    Q(student__user__first_name__icontains=search) |
                    Q(student__user__last_name__icontains=search)
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
    # https://187gwsw1-8000.inc1.devtunnels.ms/d/fee-record/initiate-payment/
    ### using custom view 
    ### Added as of 12june25 at 02:20 PM
    @action(detail=False, methods=["post"], url_path="initiate-payment")
    def initiate_payment(self, request):
        serializer = FeeRecordRazorpaySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        validated_data = serializer.validated_data
        total = validated_data['total_amount']
        late_fee = validated_data['late_fee']
        paid_amount = validated_data['paid_amount']
        amount_to_collect = total + late_fee  # This is the full due amount, not necessarily what's paid

        receipt_number = generate_receipt_number()

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            'amount': int(paid_amount * 100),  # Razorpay expects amount in paise
            'currency': 'INR',
            'payment_capture': '1',
            'receipt': receipt_number
        })

        return Response({
            'razorpay_order_id': razorpay_order['id'],
            'total_amount': float(total),
            'late_fee': float(late_fee),
            'paid_amount': float(paid_amount),
            'currency': 'INR',
            'receipt_number': receipt_number
        }, status=status.HTTP_200_OK)

    
    ### just added as of 13june25 at 11:21 AM
    # https://187gwsw1-8000.inc1.devtunnels.ms/d/fee-record/confirm-payment/
    ### ------------------------------------- ###
    # working completely fine just need to add complete fee record adding updated code here
    @action(detail=False, methods=["post"], url_path="confirm-payment")
    def confirm_payment(self, request):
        data = request.data
        required_fields = [
            "razorpay_payment_id",
            "razorpay_order_id",
            "razorpay_signature_id",
            "student_id",
            "month",
            "year_level_fees",
            "paid_amount",
            "payment_mode",
            "signature"
        ]
        missing = [field for field in required_fields if field not in data]

        if missing:
            return Response({"error": f"Missing required fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Verify Razorpay Signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": data["razorpay_order_id"],
                "razorpay_payment_id": data["razorpay_payment_id"],
                "razorpay_signature": data["razorpay_signature_id"]
            })
        except razorpay.errors.SignatureVerificationError:
            return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Save FeeRecord
        serializer = FeeRecordRazorpaySerializer(data=data)
        if serializer.is_valid():
            instance = serializer.save()

            # Serialize with full FeeRecordSerializer to return complete info
            full_data = FeeRecordSerializer(instance).data

            return Response({
                "message": "Payment successful and FeeRecord saved.",
                "fee_record": full_data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
    # corrected amount issue as of 19June25 at 02:50 PM
    # https://187gwsw1-8000.inc1.devtunnels.ms/d/fee-record/student-fee-summary/?year_level=5
    @action(detail=False, methods=["get"], url_path="student-fee-summary")
    def student_fee_summary(self, request):
        year_level = request.query_params.get("year_level")
        search = request.query_params.get("search", "").strip()

        qs = self.get_queryset()
        filters = Q()

        if year_level:
            filters &= Q(student__student_year_levels__level__id=year_level)

        if search:
            filters &= (
                Q(student__user__first_name__icontains=search) |
                Q(student__user__last_name__icontains=search)
            )

        qs = qs.filter(filters).distinct()

        summary = (
            qs.values(
                "student_id",
                "student__user__first_name",
                "student__user__last_name",
                "student__student_year_levels__level__level_name"
            )
            .annotate(
                total_amount=Coalesce(Sum("total_amount", output_field=FloatField()), Value(0.0)),
                paid_amount=Coalesce(Sum("paid_amount", output_field=FloatField()), Value(0.0)),
                late_fee=Coalesce(Sum("late_fee", output_field=FloatField()), Value(0.0))
            )
        )

        result = []
        for item in summary:
            total = item["total_amount"] + item["late_fee"]
            due = max(0, total - item["paid_amount"])

            result.append({
                "student_id": item["student_id"],
                "student_name": f"{item['student__user__first_name']} {item['student__user__last_name']}",
                "year_level": item["student__student_year_levels__level__level_name"],
                "total_amount": float(total),
                "paid_amount": float(item["paid_amount"]),
                "due_amount": float(due),
                "late_fee": float(item["late_fee"])  #  now included
            })

        return Response(result, status=status.HTTP_200_OK)
    
    # corrected amount issue as of 19June25 at 02:50 PM
    # https://187gwsw1-8000.inc1.devtunnels.ms/d/fee-record/monthly-summary/?year_level=2&month=June
    @action(detail=False, methods=["get"], url_path="monthly-summary")
    def monthly_summary(self, request):
        month = request.query_params.get("month", "").strip()
        year_level = request.query_params.get("year_level", "").strip()
        search = request.query_params.get("search", "").strip()

        qs = self.get_queryset()
        filters = Q()

        if month:
            filters &= Q(month__iexact=month)

        if year_level.isdigit():
            filters &= Q(student__student_year_levels__level__id=year_level)
        elif search:
            filters &= Q(student__student_year_levels__level__level_name__icontains=search)

        qs = qs.filter(filters).distinct()

        if not qs.exists():
            return Response({"detail": "No records found."}, status=status.HTTP_404_NOT_FOUND)

        summary = (
            qs.values(
                "month",
                "student__user__first_name",
                "student__user__last_name",
                "student__student_year_levels__level__level_name"
            )
            .annotate(
                total_amount=Coalesce(Sum("total_amount", output_field=FloatField()), Value(0.0)),
                paid_amount=Coalesce(Sum("paid_amount", output_field=FloatField()), Value(0.0)),
                late_fee=Coalesce(Sum("late_fee", output_field=FloatField()), Value(0.0))
            )
        )

        formatted_summary = []
        for item in summary:
            total = item["total_amount"] + item["late_fee"]
            due = max(0, total - item["paid_amount"])

            formatted_summary.append({
                "month": item["month"],
                "student_name": f"{item['student__user__first_name']} {item['student__user__last_name']}",
                "year_level": item["student__student_year_levels__level__level_name"],
                "total_amount": float(total),
                "paid_amount": float(item["paid_amount"]),
                "due_amount": float(due),
                "late_fee": float(item["late_fee"])  #  now included
            })

        return Response(formatted_summary, status=status.HTTP_200_OK)

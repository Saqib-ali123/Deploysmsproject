from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .models import GuardianType, Student
from .serializers import GuardianTypeSerializer, StudentSerializer
from rest_framework import status
from rest_framework.response import Response
from .serializers import GuardianSerializer
from .models import Guardian
from director.models import Role
from rest_framework.filters import SearchFilter
from rest_framework import viewsets


@api_view(["GET", "POST", "PUT", "DELETE"])
def GuardianTypeView(request, pk=None):
    if request.method == "GET":
        if pk is not None:
            try:
                guardian_type = GuardianType.objects.get(id=pk)
                serializer = GuardianTypeSerializer(guardian_type, many=False)
                return Response(serializer.data, status.HTTP_200_OK)

            except GuardianType.DoesNotExist:
                return Response(
                    {"message": "Data Not Found"}, status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {"message": "Something went wrong"},
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        else:
            guardian_types = GuardianType.objects.all()
            serializer = GuardianTypeSerializer(guardian_types, many=True)
            return Response(serializer.data, status.HTTP_200_OK)

    elif request.method == "POST":
        json_data = request.data

        if json_data.get("name", None) is None:
            return Response({"message": "Invalid Data"}, status.HTTP_400_BAD_REQUEST)

        json_data["name"] = json_data["name"].lower()
        serializer = GuardianTypeSerializer(data=json_data)

        if serializer.is_valid():

            if GuardianType.objects.filter(name=json_data["name"]).exists():
                return Response(
                    {"message": "Guardian type Already Exists"},
                    status.HTTP_400_BAD_REQUEST,
                )

            serializer.save()
            return Response(
                {"message": "GuardianType Added Successfully"}, status.HTTP_201_CREATED
            )
        return Response({"message": "Invalid Data"}, status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":

        if request.data.get("name", None) is None:
            return Response({"message": "Invalid Data"}, status.HTTP_400_BAD_REQUEST)

        request.data["name"] = request.data["name"].lower()

        try:
            guardian_type = GuardianType.objects.get(id=pk)
            serializer = GuardianTypeSerializer(
                instance=guardian_type, data=request.data, partial=True
            )

            if serializer.is_valid():

                if GuardianType.objects.filter(name=request.data["name"]).exists():
                    return Response(
                        {"message": "Guardian type Already Exists"},
                        status.HTTP_400_BAD_REQUEST,
                    )

                serializer.save()
                return Response(
                    {"message": "GuardianType updated Successfully"},
                    status.HTTP_200_OK,
                )

            return Response({"message": "Invalid Data"}, status.HTTP_400_BAD_REQUEST)

        except GuardianType.DoesNotExist:
            return Response({"message": "Data Not Found"}, status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"message": "something went wrong"},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    elif request.method == "DELETE":

        if pk is None:
            return Response(
                {"message": "Id is Required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            get = GuardianType.objects.get(id=pk)
            get.delete()
            return Response(
                {"message": "GuardianType Delete Successfully"}, status.HTTP_200_OK
            )
        except GuardianType.DoesNotExist:
            return Response({"message": "Data Not Found"}, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"message": "Something went wrong"},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StudentView(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class GuardianProfileViewSet(viewsets.ModelViewSet):
    queryset = Guardian.objects.all()
    serializer_class = GuardianSerializer
    filter_backends = [SearchFilter]
    search_fields = ['user__email','user__first_name','user__guardian_relation__phone_no']




    
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import  AttendanceSession, StudentAttendance
from .serializers import *
from django.utils.dateformat import format as date_format

# Create your views here.
class AttendanceSessionViewSet(ModelViewSet):
    queryset = AttendanceSession.objects.all()
    serializer_class = AttendanceSessionSerializer

class StudentAttendanceViewSet(ModelViewSet):
    queryset = StudentAttendance.objects.all()
    serializer_class = StudentAttendanceSerializer

class AttendanceReportViewSet(ReadOnlyModelViewSet):
    serializer_class = StudentAttendanceSerializer
    
    def get_queryset(self):
        queryset = StudentAttendance.objects.select_related('student__level', 'period')
        class_name = self.request.query_params.get('class')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')

        if class_name:
            queryset = queryset.filter(student__level__level_name__iexact=class_name)

        if month and year:
            try:
                month = int(month)
                year = int(year)
                queryset = queryset.filter(period__date__month=month, period__date__year=year)
            except ValueError:
                return StudentAttendance.objects.none()

        return queryset.order_by('student', 'period__date')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        student_attendance_map = {}
        for record in queryset:
            student_id = record.student.id
            student_name = str(record.student)
            date_str = date_format(record.period.date, "j/n/y")

            if student_id not in student_attendance_map:
                student_attendance_map[student_id] = {"Student name": student_name}

            student_attendance_map[student_id][date_str] = record.status

        final_data = list(student_attendance_map.values())
        return Response(final_data)
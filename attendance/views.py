from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import  AttendanceSession, StudentAttendance
from .serializers import *
from django.utils.dateformat import format as date_format
from datetime import date
from django.db.models import Count, Q
from rest_framework.viewsets import ViewSet
from teacher.models import TeacherYearLevel


class AttendanceSessionViewSet(ModelViewSet):
    queryset = AttendanceSession.objects.all()
    serializer_class = AttendanceSessionSerializer

class StudentAttendanceViewSet(ModelViewSet):
    queryset = StudentAttendance.objects.all()
    serializer_class = StudentAttendanceSerializer

class AttendanceReportViewSet(ReadOnlyModelViewSet):
    serializer_class = StudentAttendanceSerializer
    
    def get_queryset(self):
        queryset = StudentAttendance.objects.select_related('student__level', 'session_id')
        class_name = self.request.query_params.get('class')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')

        if class_name:
            queryset = queryset.filter(student__level__level_name__iexact=class_name)
        if month and year:
            try:
                month = int(month)
                year = int(year)
                queryset = queryset.filter(
                    session_id__date__month=month,
                    session_id__date__year=year
                )
            except ValueError:
                return StudentAttendance.objects.none()

        return queryset.order_by('student', 'session_id__date')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        student_attendance_map = {}

        for record in queryset:
            student_id = record.student.id
            student_name = str(record.student)
            date_str = date_format(record.session_id.date, "j/n/y")

            if student_id not in student_attendance_map:
                student_attendance_map[student_id] = {"Student name": student_name}

            student_attendance_map[student_id][date_str] = record.status

        final_data = list(student_attendance_map.values())
        return Response(final_data)
    


class DirectorAttendanceDashboard(ModelViewSet):
    serializer_class = StudentAttendanceSerializer
    def list(self, request):
        today = date.today()
        total_students = Student.objects.count()
        present_today = StudentAttendance.objects.filter(marked_at=today, status='P').count()
        overall_percentage = (present_today / total_students * 100) if total_students else 0

        
        all_classes = YearLevel.objects.all()
        class_wise = {}

        for cls in all_classes:
            session = AttendanceSession.objects.filter(year_level=cls, date=today).first()
            if session:
                attendances = StudentAttendance.objects.filter(session_id=session)
                total = attendances.count()
                present = attendances.filter(status='P').count()
                percentage = (present / total * 100) if total else 0
            else:
                percentage = 0.0
            class_wise[cls.level_name] = f"{percentage:.0f}%"

        return Response({
            "overall": f"{overall_percentage:.1f}%",
            "class_wise": class_wise
        })
        
        
class TeacherAttendanceDashboard(ViewSet):
    def list(self, request):
        today = date.today()
        month = today.month
        year = today.year

        class_name = request.query_params.get("class_name")  
        student_levels = StudentYearLevel.objects.all()
        if class_name:
            student_levels = student_levels.filter(level__level_name__iexact=class_name)

        result = []

        for syl in student_levels:
            attendance_qs = StudentAttendance.objects.filter(student=syl)
            monthly = attendance_qs.filter(marked_at__year=year, marked_at__month=month)
            monthly_total = monthly.count()
            monthly_present = monthly.filter(status='P').count()
            monthly_percentage = (monthly_present / monthly_total * 100) if monthly_total else 0.0

            yearly = attendance_qs.filter(marked_at__year=year)
            yearly_total = yearly.count()
            yearly_present = yearly.filter(status='P').count()
            yearly_percentage = (yearly_present / yearly_total * 100) if yearly_total else 0.0

            result.append({
                "student_name": syl.student,  
                "class_name": syl.level.level_name,
                "monthly_percentage": round(monthly_percentage, 1),
                "yearly_percentage": round(yearly_percentage, 1)
            })

        serializer = StudentAttendancePercentSerializer(result, many=True)
        return Response(serializer.data)
    

class StudentOwnAttendanceViewSet(ViewSet):
    def retrieve(self, request, pk=None):  
        today = date.today()
        month = today.month
        year = today.year

        try:
            student_level = StudentYearLevel.objects.get(id=pk)
        except StudentYearLevel.DoesNotExist:
            return Response({"error": "Student not found."}, status=404)

        attendance_qs = StudentAttendance.objects.filter(student=student_level)

        monthly = attendance_qs.filter(marked_at__year=year, marked_at__month=month)
        yearly = attendance_qs.filter(marked_at__year=year)

        monthly_present = monthly.filter(status='P').count()
        yearly_present = yearly.filter(status='P').count()

        monthly_total = monthly.count()
        yearly_total = yearly.count()

        monthly_percentage = (monthly_present / monthly_total * 100) if monthly_total else 0.0
        yearly_percentage = (yearly_present / yearly_total * 100) if yearly_total else 0.0

        return Response({
            "student_name": str(student_level.student),  
            "class_name": student_level.level.level_name,
            "monthly_percentage": round(monthly_percentage, 1),
            "yearly_percentage": round(yearly_percentage, 1)
        })
        
        
        

class GuardianChildrenAttendanceViewSet(ViewSet):
    def list(self, request):
        guardian_id = request.query_params.get("guardian_id")
        if not guardian_id:
            return Response({"error": "guardian_id is required"}, status=400)

        try:
            guardian = Guardian.objects.get(id=guardian_id)
        except Guardian.DoesNotExist:
            return Response({"error": "Guardian not found"}, status=404)

        student_links = StudentGuardian.objects.filter(guardian=guardian)
        children = [link.student for link in student_links]

        today = date.today()
        current_month = today.month
        current_year = today.year

        response_data = []

        for student in children:
            try:
                year_level = StudentYearLevel.objects.get(student=student)
            except StudentYearLevel.DoesNotExist:
                continue

            total_month = StudentAttendance.objects.filter(
                student=year_level,
                marked_at__year=current_year,
                marked_at__month=current_month
            ).count()

            present_month = StudentAttendance.objects.filter(
                student=year_level,
                marked_at__year=current_year,
                marked_at__month=current_month,
                status='P'
            ).count()

            total_year = StudentAttendance.objects.filter(
                student=year_level,
                marked_at__year=current_year
            ).count()

            present_year = StudentAttendance.objects.filter(
                student=year_level,
                marked_at__year=current_year,
                status='P'
            ).count()

            monthly_percentage = round((present_month / total_month) * 100, 2) if total_month else 0.0
            yearly_percentage = round((present_year / total_year) * 100, 2) if total_year else 0.0

            response_data.append({
                'student_name': f"{student.user.first_name} {student.user.last_name}",
                'monthly_percentage': monthly_percentage,
                'yearly_percentage': yearly_percentage,
            })

        return Response(response_data)
    
    
    
class TeacherYearLevelList(APIView):
    def get(self, request, teacher_id):
        levels = TeacherYearLevel.objects.filter(teacher_id=teacher_id).select_related('year_level')
        data = [{'id': l.year_level.id, 'name': str(l.year_level)} for l in levels]
        return Response(data)
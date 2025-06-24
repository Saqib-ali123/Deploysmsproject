from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import   StudentAttendance
from .serializers import *
from django.utils.dateformat import format as date_format
from datetime import date,datetime, timedelta
from django.db.models import Count, Q
from rest_framework.viewsets import ViewSet
from teacher.models import TeacherYearLevel
from student.models import Guardian,StudentGuardian, StudentYearLevel, Student


class StudentAttendanceViewSet(ModelViewSet):
    queryset = StudentAttendance.objects.all()
    serializer_class = StudentAttendanceSerializer
    

class MultipleAttendanceViewSet1(ModelViewSet):
    queryset = StudentAttendance.objects.all()
    serializer_class = StudentAttendanceSerializer

    def create(self, request, *args, **kwargs):
        data = request.data

        # ➤ Date Handling
        try:
            marked_at_str = data.get("marked_at", None)
            if marked_at_str:
                marked_at = datetime.strptime(marked_at_str, "%Y-%m-%d").date()
            else:
                marked_at = date.today()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # ➤ Teacher Check
        teacher_id = data.get("teacher_id")
        if not teacher_id:
            return Response({"error": "teacher_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            teacher = Teacher.objects.get(id=teacher_id)
        except Teacher.DoesNotExist:
            return Response({"error": "Invalid teacher_id."}, status=status.HTTP_404_NOT_FOUND)

        # ➤ Validate All Students First
        allowed_statuses = {'P', 'A', 'L'}
        conflict_students = []

        for status_code in allowed_statuses:
            student_ids = data.get(status_code, [])
            for sid in student_ids:
                if StudentAttendance.objects.filter(student_id=sid, marked_at=marked_at).exists():
                    conflict_students.append(sid)

        # ➤ If Any Conflict Found
        if conflict_students:
            return Response({
                "error": "Attendance already exists for the following student(s) on this date."
            }, status=status.HTTP_400_BAD_REQUEST)

        # ➤ Proceed with Attendance Creation
        created_records = []
        for status_code in allowed_statuses:
            student_ids = data.get(status_code, [])
            for sid in student_ids:
                try:
                    student = Student.objects.get(id=sid)
                    year_level = student.student_year_levels.last().level

                    attendance = StudentAttendance.objects.create(
                        student=student,
                        status=status_code,
                        marked_at=marked_at,
                        teacher=teacher,
                        year_level=year_level
                    )
                    created_records.append(attendance)
                except Student.DoesNotExist:
                    continue

        serializer = self.get_serializer(created_records, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AttendanceReportViewSet(ReadOnlyModelViewSet):
    serializer_class = StudentAttendanceSerializer

    def get_queryset(self):
        queryset = StudentAttendance.objects.select_related('student', 'year_level')
        class_name = self.request.query_params.get('class')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')

        if class_name:
            queryset = queryset.filter(year_level__level_name__iexact=class_name)

        if month and year:
            try:
                month = int(month)
                year = int(year)
                queryset = queryset.filter(
                    marked_at__month=month,
                    marked_at__year=year
                )
            except ValueError:
                return StudentAttendance.objects.none()

        return queryset.order_by('student', 'marked_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        student_attendance_map = {}

        for record in queryset:
            student_id = record.student.id
            student_name = str(record.student)
            date_obj = record.marked_at
            date_str = date_format(date_obj, "j/n/y") + f" ({date_obj.strftime('%A')})"

            if student_id not in student_attendance_map:
                student_attendance_map[student_id] = {"Student name": student_name}

            student_attendance_map[student_id][date_str] = record.status

        final_data = list(student_attendance_map.values())
        return Response(final_data)

class DirectorAttendanceDashboard(ViewSet):
    def list(self, request):
        date_str = request.query_params.get("date")
        try:
            if date_str:
                marked_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                marked_date = date.today()              
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        # Step 2: Get attendance summary
        total_students = Student.objects.count()
        present_today = StudentAttendance.objects.filter(marked_at=marked_date, status='P').count()
        overall_percentage = (present_today / total_students * 100) if total_students else 0

        # Step 3: Class-wise breakdown
        class_wise_data = []
        all_classes = YearLevel.objects.all()

        for cls in all_classes:
            attendances = StudentAttendance.objects.filter(marked_at=marked_date, year_level=cls)
            total = attendances.count()
            present = attendances.filter(status='P').count()
            percentage = (present / total * 100) if total else 0

            class_wise_data.append({
                "class_name": cls.level_name,
                "present": present,
                "total": total,
                "percentage": f"{percentage:.1f}%"
            })

        return Response({
            "date": marked_date.strftime("%Y-%m-%d"),
            "overall_attendance": {
                "present": present_today,
                "total": total_students,
                "percentage": f"{overall_percentage:.1f}%"
            },
            "class_wise_attendance": class_wise_data
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
            attendance_qs = StudentAttendance.objects.filter(student=syl.student)

            # Monthly summary
            monthly = attendance_qs.filter(marked_at__year=year, marked_at__month=month)
            m_present = monthly.filter(status='P').count()
            m_absent = monthly.filter(status='A').count()
            m_leave = monthly.filter(status='L').count()
            m_total = monthly.count()
            m_percentage = (m_present / m_total * 100) if m_total else 0.0

            # Yearly summary
            yearly = attendance_qs.filter(marked_at__year=year)
            y_present = yearly.filter(status='P').count()
            y_absent = yearly.filter(status='A').count()
            y_leave = yearly.filter(status='L').count()
            y_total = yearly.count()
            y_percentage = (y_present / y_total * 100) if y_total else 0.0

            result.append({
                "student_name": str(syl.student),
                "class_name": syl.level.level_name,
                "monthly_percentage": round(m_percentage, 1),
                "yearly_percentage": round(y_percentage, 1),
                "monthly_summary": {
                    "present": m_present,
                    "absent": m_absent,
                    "leave": m_leave,
                    "total_days": m_total
                },
                "yearly_summary": {
                    "present": y_present,
                    "absent": y_absent,
                    "leave": y_leave,
                    "total_days": y_total
                }
            })

        return Response(result)   
class StudentOwnAttendanceViewSet(ViewSet):
    def retrieve(self, request, pk=None):  
        today = date.today()
        month = today.month
        year = today.year

        try:
            student_level = StudentYearLevel.objects.get(id=pk)
        except StudentYearLevel.DoesNotExist:
            return Response({"error": "Student not found."}, status=404)

        attendance_qs = StudentAttendance.objects.filter(student=student_level.student)

        # Monthly summary
        monthly = attendance_qs.filter(marked_at__year=year, marked_at__month=month)
        m_present = monthly.filter(status='P').count()
        m_absent = monthly.filter(status='A').count()
        m_leave = monthly.filter(status='L').count()
        m_total = monthly.count()
        m_percentage = (m_present / m_total * 100) if m_total else 0.0

        # Yearly summary
        yearly = attendance_qs.filter(marked_at__year=year)
        y_present = yearly.filter(status='P').count()
        y_absent = yearly.filter(status='A').count()
        y_leave = yearly.filter(status='L').count()
        y_total = yearly.count()
        y_percentage = (y_present / y_total * 100) if y_total else 0.0

        return Response({
            "student_name": str(student_level.student),
            "class_name": student_level.level.level_name,
            "monthly_percentage": round(m_percentage, 1),
            "yearly_percentage": round(y_percentage, 1),
            "monthly_summary": {
                "present": m_present,
                "absent": m_absent,
                "leave": m_leave,
                "total_days": m_total
            },
            "yearly_summary": {
                "present": y_present,
                "absent": y_absent,
                "leave": y_leave,
                "total_days": y_total
            }
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

            # Monthly
            monthly_qs = StudentAttendance.objects.filter(
                student=student,
                marked_at__year=current_year,
                marked_at__month=current_month
            )
            m_total = monthly_qs.count()
            m_present = monthly_qs.filter(status='P').count()
            m_absent = monthly_qs.filter(status='A').count()
            m_leave = monthly_qs.filter(status='L').count()
            m_percent = round((m_present / m_total) * 100, 1) if m_total else 0.0

            # Yearly
            yearly_qs = StudentAttendance.objects.filter(
                student=student,
                marked_at__year=current_year
            )
            y_total = yearly_qs.count()
            y_present = yearly_qs.filter(status='P').count()
            y_absent = yearly_qs.filter(status='A').count()
            y_leave = yearly_qs.filter(status='L').count()
            y_percent = round((y_present / y_total) * 100, 1) if y_total else 0.0

            response_data.append({
                'student_name': f"{student.user.first_name} {student.user.last_name}",
                'class_name': year_level.level.level_name,
                'monthly_summary': {
                    "present": m_present,
                    "absent": m_absent,
                    "leave": m_leave,
                    "total_days": m_total,
                    "percentage": f"{m_percent}%"
                },
                'yearly_summary': {
                    "present": y_present,
                    "absent": y_absent,
                    "leave": y_leave,
                    "total_days": y_total,
                    "percentage": f"{y_percent}%"
                }
            })

        return Response({
            "guardian_id": guardian.id,
            "total_children": len(response_data),
            "children": response_data
        })
    
    
    
class TeacherYearLevelList(APIView):
    def get(self, request, teacher_id):
        levels = TeacherYearLevel.objects.filter(teacher_id=teacher_id).select_related('year_level')
        data = [{'id': l.year_level.id, 'name': str(l.year_level)} for l in levels]
        return Response(data)
    
class BulkHolidayAttendanceViewSet(ViewSet):
    def list(self, request):
        holidays = Holiday.objects.all().order_by('-start_date')
        serializer = HolidaySerializer(holidays, many=True)
        return Response(serializer.data)
    def create(self, request):
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')
        title = request.data.get('title', 'Unnamed Holiday')
        teacher_id = request.data.get('teacher_id')

        if not start_date_str or not end_date_str:
            return Response({"error": "Start and end date are required."}, status=400)

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        if start_date > end_date:
            return Response({"error": "Start date must be before end date."}, status=400)

        # Save Holiday record
        Holiday.objects.create(
            title=title,
            start_date=start_date,
            end_date=end_date
        )

        # Get Teacher
        try:
            teacher = Teacher.objects.get(id=teacher_id)
        except Teacher.DoesNotExist:
            return Response({"error": "Teacher not found."}, status=404)

        students = Student.objects.all()
        dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        count = 0
        for student in students:
            try:
                syl = StudentYearLevel.objects.get(student=student)
                for date in dates:
                    if not StudentAttendance.objects.filter(student=student, marked_at=date).exists():
                        StudentAttendance.objects.create(
                            student=student,
                            status='H',
                            marked_at=date,
                            teacher=teacher,
                            year_level=syl.level
                        )
                        count += 1
            except StudentYearLevel.DoesNotExist:
                continue

        return Response({
            "message": f"{count} holiday attendance records created from {start_date} to {end_date}."
        }, status=201)
        
        
        


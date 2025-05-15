from django.shortcuts import render

# Create your views here.
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Teacher
from .serializers import TeacherSerializer
from rest_framework import filters
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from director.models import *
from django.db.models import Prefetch


class TeacherView(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


    filter_backends = [filters.SearchFilter]
    search_fields = ['user__email', 'user__first_name', 'phone_no']
    
    # @action(detail=True, methods=['post'], url_path='assign-teacher-details')
    # def assign_teacher_details(self, request, pk=None):
    #     teacher = self.get_object()
    #     print(f"Fetched teacher: {teacher}")

    #     yearlevel_id = request.data.get("yearlevel_id")
    #     subject_ids = request.data.get("subject_ids", [])
    #     period_ids = request.data.get("period_ids", [])

    #     print(f"Request Data: yearlevel_id={yearlevel_id}, subject_ids={subject_ids}, period_ids={period_ids}")

    #     # Validate yearlevel_id
    #     if not yearlevel_id:
    #         print("Missing yearlevel_id.")
    #         return Response({"error": "yearlevel_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    #     try:
    #         yearlevel_id = int(yearlevel_id)
    #         subject_ids = list(map(int, subject_ids))
    #         period_ids = list(map(int, period_ids))
    #     except ValueError:
    #         print("ID format is invalid.")
    #         return Response({"error": "IDs must be integers."}, status=status.HTTP_400_BAD_REQUEST)

    #     # Get year level
    #     yearlevel = YearLevel.objects.filter(id=yearlevel_id).first()
    #     if not yearlevel:
    #         print(f"YearLevel with ID {yearlevel_id} not found.")
    #         return Response({"error": "Invalid yearlevel_id."}, status=status.HTTP_404_NOT_FOUND)

    #     print(f"Found YearLevel: {yearlevel.level_name}")

    #     # Fetch periods from DB
    #     periods = Period.objects.filter(id__in=period_ids)
    #     print(f"Fetched periods from DB: {[p.id for p in periods]}")

    #     if not periods.exists():
    #         print("No valid periods found.")
    #         return Response({"error": "No valid periods found."}, status=status.HTTP_400_BAD_REQUEST)

    #     # Check current and new assignments through ClassPeriod
    #     existing_period_ids = ClassPeriod.objects.filter(teacher=teacher).values_list("start_time__id", flat=True)
    #     print(f"Existing period IDs: {list(existing_period_ids)}")

    #     new_periods = periods.exclude(id__in=existing_period_ids)
    #     total_periods = len(existing_period_ids) + new_periods.count()
    #     print(f"New periods to assign: {[p.id for p in new_periods]} | Total after assignment: {total_periods}")

    #     if total_periods > 6:
    #         print("Exceeded period assignment limit.")
    #         return Response({"error": "Teacher can be assigned a maximum of 6 periods."}, status=status.HTTP_400_BAD_REQUEST)

    #     # Get subjects
    #     subjects = Subject.objects.filter(id__in=subject_ids)
    #     if not subjects.exists():
    #         print("No valid subjects found.")
    #         return Response({"error": "No valid subjects found."}, status=status.HTTP_400_BAD_REQUEST)

    #     print(f"Subjects found: {[s.subject_name for s in subjects]}")

    #     # Assign teacher and subjects dynamically
    #     for period in new_periods:
    #         for subject in subjects:
    #             # Here, you would implement your logic to associate the teacher with this period.
    #             print(f"Assigning teacher {teacher.user.get_full_name()} to Period {period.id} with subject {subject.subject_name}")

    #         print(f"Assigned teacher {teacher.user.get_full_name()} to period {period.id} with subjects {[s.subject_name for s in subjects]}")

    #     # Link teacher to year level
    #     tyl_obj, created = TeacherYearLevel.objects.get_or_create(teacher=teacher, year_level=yearlevel)
    #     print(f"Teacher-YearLevel mapping {'created' if created else 'already exists'}: {tyl_obj}")

    #     response_data = {
    #         "message": "Teacher details assigned successfully.",
    #         "teacher": teacher.user.get_full_name() if teacher.user else str(teacher),
    #         "year_level": yearlevel.level_name,
    #         "subjects": [s.subject_name for s in subjects],
    #         "assigned_periods": [{
    #             "id": p.id,
    #             "name": p.name,
    #             "year": str(p.year),  
    #             "start_time": p.start_period_time,
    #             "end_time": p.end_period_time
    #         } for p in new_periods]
    #     }

    #     print("Response data prepared:", response_data)
    #     return Response(response_data)
    
    


    

    @action(detail=False, methods=['post'], url_path='assign-teacher-details')
    def assign_teacher_details(self, request):
        teacher_id = request.data.get("teacher_id")
        yearlevel_id = request.data.get("yearlevel_id")
        subject_ids = request.data.get("subject_ids", [])
        period_ids = request.data.get("period_ids", [])

        # Validate teacher
        if not teacher_id:
            return Response({"error": "teacher_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            teacher = Teacher.objects.get(id=teacher_id)
        except Teacher.DoesNotExist:
            return Response({"error": "Invalid teacher_id."}, status=status.HTTP_404_NOT_FOUND)

        # Validate year level
        if not yearlevel_id:
            return Response({"error": "yearlevel_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            yearlevel = YearLevel.objects.get(id=yearlevel_id)
        except YearLevel.DoesNotExist:
            return Response({"error": "Invalid yearlevel_id."}, status=status.HTTP_404_NOT_FOUND)

        # Validate subjects
        if not subject_ids:
            return Response({"error": "At least one subject_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        subjects = Subject.objects.filter(id__in=subject_ids)
        if subjects.count() != len(subject_ids):
            return Response({"error": "One or more invalid subject_ids."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate periods
        if not period_ids:
            return Response({"error": "At least one period_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        periods = Period.objects.filter(id__in=period_ids)
        if periods.count() != len(period_ids):
            return Response({"error": "One or more invalid period_ids."}, status=status.HTTP_400_BAD_REQUEST)

        # Check teacher's current period load
        existing_classperiods = ClassPeriod.objects.filter(teacher=teacher)
        if existing_classperiods.count() + len(subject_ids) > 6:
            return Response({"error": "Teacher cannot be assigned more than 6 periods."}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent duplicate assignments of the same subject to the same period
        assigned = []
        for subject in subjects:
            # Ensure the teacher has only one period assigned for each subject
            subject_period_assigned = ClassPeriod.objects.filter(teacher=teacher, subject=subject).exists()
            if subject_period_assigned:
                return Response(
                    {"error": f"Teacher is already assigned {subject.subject_name} in a period."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            for period in periods:
                # Assign only one period for each subject per teacher
                if not ClassPeriod.objects.filter(teacher=teacher, subject=subject).exists():
                    # Assign the teacher to the subject and period
                    cp = ClassPeriod.objects.create(
                        teacher=teacher,
                        subject=subject,
                        term=Term.objects.first(),  
                        start_time=period,  # Assign Period instance to start_time
                        end_time=period,  # Assign Period instance to end_time
                        classroom=ClassRoom.objects.first(),  # Using the first available classroom
                        name=f"{subject.subject_name} - {period.name}"
                    )
                    assigned.append({
                        "subject": subject.subject_name,
                        "period": period.name,
                        "time": f"{period.start_period_time} - {period.end_period_time}"
                    })
                    break  # Assign only one period per subject for the teacher

        # Link teacher to year level
        TeacherYearLevel.objects.get_or_create(teacher=teacher, year_level=yearlevel)

        # Return detailed response
        return Response({
            "message": "Teacher assigned successfully.",
            "teacher": f"{teacher.user.first_name} {teacher.user.last_name}",
            "year_level": yearlevel.level_name,
            "assigned_subjects_periods": assigned
        }, status=status.HTTP_200_OK)

















    # @action(detail=True, methods=['post'], url_path='assign-teacher-details')
    # def assign_teacher_details(self, request, pk=None):
    #     teacher = self.get_object()  

    #     yearlevel_id = request.data.get("yearlevel_id")
    #     subject_ids = request.data.get("subject_ids", [])
    #     period_ids = request.data.get("period_ids", [])

    #     print(f"Received data - YearLevel ID: {yearlevel_id}, Subject IDs: {subject_ids}, Period IDs: {period_ids}")

    #     if not yearlevel_id:
    #         return Response({"error": "yearlevel_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    #     # Ensure IDs are integers
    #     try:
    #         subject_ids = list(map(int, subject_ids))
    #         period_ids = list(map(int, period_ids))
    #         yearlevel_id = int(yearlevel_id)
    #     except ValueError:
    #         return Response({"error": "Invalid ID format."}, status=status.HTTP_400_BAD_REQUEST)

    #     # Fetch the YearLevel instance
    #     yearlevel = YearLevel.objects.filter(id=yearlevel_id).first()
    #     if not yearlevel:
    #         return Response({"error": "Invalid yearlevel_id."}, status=status.HTTP_404_NOT_FOUND)

    #     print(f"YearLevel found: {yearlevel.level_name}")

    #     # Fetch periods using period_ids passed in the request
    #     periods = ClassPeriod.objects.filter(id__in=period_ids)
    #     print(f"All ClassPeriod IDs in DB: {list(ClassPeriod.objects.values_list('id', flat=True))}")
    #     print(f"Periods found: {periods}")

    #     if not periods.exists():
    #         return Response({"error": "No valid periods found for the provided IDs."}, status=status.HTTP_400_BAD_REQUEST)

    #     current_period_ids = teacher.classperiod_set.values_list("id", flat=True)
    #     print(f"Currently assigned periods: {list(current_period_ids)}")

    #     new_period_ids = [pid for pid in period_ids if pid not in current_period_ids]
    #     print(f"New periods to assign: {new_period_ids}")

    #     if len(current_period_ids) + len(new_period_ids) > 6:
    #         return Response({"error": "Teacher can only be assigned a maximum of 6 periods."}, status=status.HTTP_400_BAD_REQUEST)

    #     new_periods = periods.filter(id__in=new_period_ids)
    #     print(f"New periods retrieved: {new_periods}")

    #     subjects = Subject.objects.filter(id__in=subject_ids)
    #     print(f"Subjects found: {subjects}")

    #     if not subjects.exists():
    #         return Response({"error": "No valid subjects found for the provided IDs."}, status=status.HTTP_400_BAD_REQUEST)

    #     for period in new_periods:
    #         period.teacher = teacher
    #         period.save()
    #         period.subject.set(subjects)

    #     TeacherYearLevel.objects.get_or_create(teacher=teacher, year_level=yearlevel)

    #     assigned_subjects = [subject.subject_name for subject in subjects]
    #     assigned_periods = [{
    #         "id": period.id,
    #         "name": period.name,
    #         "year": period.year,
    #         "start_period_time": period.start_period_time,
    #         "end_period_time": period.end_period_time
    #     } for period in new_periods]

    #     return Response({
    #         "message": "Teacher details assigned successfully.",
    #         "teacher": teacher.user.get_full_name() if teacher.user else str(teacher),
    #         "assigned_year_level": yearlevel.level_name,
    #         "subjects": assigned_subjects,
    #         "periods": assigned_periods
    #     })


    @action(detail=False, methods=['get'], url_path='all-teacher-assignments')
    def get_all_teacher_assignments(self, request):
        teachers = Teacher.objects.prefetch_related(
            'year_levels',  # Fetch the teacher's YearLevel through the ManyToMany relationship
            'classperiod_set',  # Fetch periods associated with the teacher
        ).all()

        response_data = []

        for teacher in teachers:
            yearlevel_map = {}

            # Populating the yearlevel_map with available year levels for this teacher
            for tyl in teacher.year_levels.all():
                yearlevel_map[tyl.id] = {
                    "year_level_id": tyl.id,
                    "year_level_name": tyl.level_name,
                    "periods": []
                }

            # Process each period and categorize it into the corresponding year level
            for period in teacher.classperiod_set.all():
                matched = False
                for y_id in yearlevel_map:
                    # If the period matches a year level, assign it
                    if not matched:
                        yearlevel_map[y_id]["periods"].append({
                            'period_id': period.id,
                            'period_name': period.name,
                            'start_time': period.start_time.start_period_time.strftime("%H:%M") if period.start_time else None,
                            'end_time': period.end_time.end_period_time.strftime("%H:%M") if period.end_time else None,
                            'subject_id': period.subject.id,
                            'subject_name': period.subject.subject_name
                        })
                        matched = True
                        break

                # If no match (i.e., the period doesn't belong to any year level), we can skip it or handle it differently.
                if not matched:
                    # You can skip this or handle it by putting it under an 'Unmapped' category if needed.
                    # I am not adding 'Unmapped' handling in this simplified version.
                    pass

            # Add the teacher's information to the response data
            response_data.append({
                'teacher_id': teacher.id,
                'teacher_name': teacher.user.get_full_name() if teacher.user else str(teacher),
                'total_assigned_periods': teacher.classperiod_set.count(),
                'max_periods_allowed': 6,
                'assignments': list(yearlevel_map.values())
            })

        return Response(response_data, status=status.HTTP_200_OK)
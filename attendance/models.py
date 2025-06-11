from django.db import models
from director.models import *
from teacher.models import *


class AttendanceSession(models.Model):
    date = models.DateField()
    year_level=models.ForeignKey(YearLevel,on_delete=models.CASCADE)

    class Meta:
        unique_together = ('date', 'year_level')

    def __str__(self):
        return f"{self.date} - {self.year_level}"
    
    
class StudentAttendance(models.Model):
    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Leave'),
    ]

    session_id = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name="attendances")
    student = models.ForeignKey(StudentYearLevel, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    marked_at = models.DateField()
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE)

    class Meta:
        unique_together = ('session_id', 'student')
    def __str__(self):
        return f"{self.student} -{self.status}"

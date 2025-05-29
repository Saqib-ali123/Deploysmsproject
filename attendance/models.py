from django.db import models
from director.models import *


class AttendanceSession(models.Model):
    date = models.DateField()
    class_period = models.ForeignKey(ClassPeriod, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('date', 'class_period')

    def __str__(self):
        return f"{self.date} - {self.class_period}"
    
    
class StudentAttendance(models.Model):
    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Leave'),
    ]

    period = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name="attendances")
    student = models.ForeignKey(StudentYearLevel, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    marked_at = models.DateField()

    class Meta:
        unique_together = ('period', 'student')
    def __str__(self):
        return f"{self.student} -{self.status}"

from django.db import models
from director.models import *
from teacher.models import *


class Holiday(models.Model):
    title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        if self.start_date == self.end_date:
            return f"{self.title} ({self.start_date})"
        return f"{self.title} ({self.start_date} to {self.end_date})"

    
    
class StudentAttendance(models.Model):
    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Leave'),
        ('H','Holiday')
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    marked_at = models.DateField()
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE)
    year_level=models.ForeignKey(YearLevel,on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.student} -{self.status}"

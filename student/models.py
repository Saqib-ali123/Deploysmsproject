from django.db import models
from teacher.models import *
from authentication.models import User
from decimal import Decimal


# Create your models here.


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    father_name=models.CharField(max_length=250,null=True, blank=True)
    mother_name=models.CharField(max_length=250,null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=50,null=True, blank=True)
    # enrolment_date = models.DateField(null=True, blank=True)
    religion = models.CharField(max_length=50,null=True, blank=True)
    category = models.CharField(
    max_length=10,
    choices=[
        ('SC', 'Scheduled Caste'),
        ('ST', 'Scheduled Tribe'),
        ('OBC', 'Other Backward Class'),
        ('GEN', 'General')
    ],
    default='GEN'
)

    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    blood_group = models.CharField(max_length=5,null=True, blank=True)
    number_of_siblings = models.IntegerField(null=True, blank=True)
    roll_number = models.CharField(max_length=50, null=True, blank=True) 
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    scholar_number = models.CharField(max_length=50, unique=True, null=True, blank=True)


    # Many-to-many relationship with classPeriod
    classes = models.ManyToManyField(
        "director.classPeriod", blank=False, related_name="Student"
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} "

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        db_table = "Student"



class Guardian(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="guardian_relation"
    )
    phone_no = models.CharField(max_length=50,null=True, blank=True)
    annual_income = models.IntegerField(null=True, blank=True)
    
    means_of_livelihood = models.CharField(
        max_length=10,
        choices=[
            ('Govt', 'Government'),
            ('Non-Govt', 'Non-Government'),
        ],
        default='Govt'
    )
    
    qualification = models.CharField(max_length=300,null=True, blank=True)
    occupation = models.CharField(max_length=300,null=True, blank=True)
    designation = models.CharField(max_length=300,null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}" if self.user else "No User"

    class Meta:
        verbose_name = "Guardian"
        verbose_name_plural = "Guardians"
        db_table = "Guardian"


class GuardianType(models.Model):
    name = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "GuardianType"
        verbose_name_plural = "GuardianTypes"
        db_table = "GuardianType"


# ---- RELATION BETWEEN STUDENT, GUARDIAN AND GUARDIAN TYPE ( ONE TO MANY ) -------------


class StudentGuardian(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    guardian = models.ForeignKey(Guardian, on_delete=models.DO_NOTHING)
    guardian_type = models.ForeignKey(GuardianType, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"{self.student} - {self.guardian} - {self.guardian_type}"

    class Meta:
        verbose_name = "StudentGuardian"
        verbose_name_plural = "StudentGuardians"
        db_table = "StudentGuardian"


class StudentYearLevel(models.Model):
    # student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='student_year_levels'  # Add this
    )
    level = models.ForeignKey("director.YearLevel", on_delete=models.DO_NOTHING)
    year = models.ForeignKey("director.SchoolYear", on_delete=models.DO_NOTHING)

    def __str__(self):

        return f"{self.student} - {self.level} "

    class Meta:
        verbose_name = "StudentYearLevel"
        verbose_name_plural = "StudentYearLevels"
        db_table = "StudentYearLevel"

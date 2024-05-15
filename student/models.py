from django.db import models
from teacher.models import *
from authentication.models import User


# Create your models here.


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    date_of_birth = models.DateField(null=False)
    gender = models.CharField(max_length=50)
    enrolment_date = models.DateField(null=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} {self.user.email}"

    # -------- Relation Between Student AND class Period  ( MANY TO MANY ) ----------------

    classes = models.ManyToManyField(
        "director.ClassPeriod", blank=False, related_name="Student"
    )

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        db_table = "Student"


class Guardian(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='guardian_relation')
    phone_no = models.CharField(max_length=50, null=False)
    

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

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
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    level = models.ForeignKey("director.YearLevel", on_delete=models.DO_NOTHING)
    year = models.ForeignKey("director.SchoolYear", on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"{self.student} - {self.level} - {self.year}"

    class Meta:
        verbose_name = "StudentYearLevel"
        verbose_name_plural = "StudentYearLevels"
        db_table = "StudentYearLevel"

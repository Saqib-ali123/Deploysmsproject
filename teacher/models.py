from django.db import models
from authentication.models import User


# Create your models here.
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    phone_no = models.CharField(max_length=100)
    gender = models.CharField(max_length=50)
    adhaar_no = models.BigIntegerField()
    pan_no = models.BigIntegerField()
    qualification = models.CharField(max_length=250)

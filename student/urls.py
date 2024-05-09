from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Define the router for the StudentView
router = DefaultRouter()
router.register(r'students', StudentView)


urlpatterns = [
    path("guardian-types/", GuardianTypeView, name="guardian-type"),
    path("guardian-type/<int:pk>/", GuardianTypeView, name="guardian-type-details"),
      path('', include(router.urls)), 
]
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from student.views import StudentView

from django.contrib import admin

# Define the router for the StudentView
router = DefaultRouter()
router.register(r'students', StudentView)

# Combine the router's URL patterns with the admin URL pattern
urlpatterns = [
    path('admin/', admin.site.urls),  # Admin URL pattern
    path('', include(router.urls)),   # Router's URL patterns
]

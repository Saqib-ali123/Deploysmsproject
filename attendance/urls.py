from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'attendancesession', AttendanceSessionViewSet, basename='attendancesession')
router.register(r'studentattendance', StudentAttendanceViewSet, basename='studentattendance')
router.register(r'api/report', AttendanceReportViewSet, basename='attendance-report')

urlpatterns = [
    path('', include(router.urls)),
]
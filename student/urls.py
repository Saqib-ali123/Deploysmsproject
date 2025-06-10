from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'students', StudentView)
router.register(r'gaurdian', GuardianProfileView)
router.register(r'studentyearlevels', StudentYearLevelView)   # As of 29May25 at 02:30 PM


urlpatterns = [
    path("guardian-types/", GuardianTypeView, name="guardian-type"),
    path("guardian-type/<int:pk>/", GuardianTypeView, name="guardian-type-details"),
      path('', include(router.urls)), 
]



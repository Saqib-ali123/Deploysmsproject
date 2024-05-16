from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'students', StudentView)


urlpatterns = [
    path("guardian-types/", GuardianTypeView, name="guardian-type"),
    path("guardian-type/<int:pk>/", GuardianTypeView, name="guardian-type-details"),
      path('', include(router.urls)), 
]

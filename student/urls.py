from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from student.views import StudentView
# Define the router for the StudentView
router = DefaultRouter()
router.register(r'students', StudentView)


urlpatterns = [
    path("guardian-types/", GuardianTypeView, name="guardian-type"),
    path("guardian-type/<int:pk>/", GuardianTypeView, name="guardian-type-details"),
      path('', include(router.urls)), 
]




# Define the router for the StudentView
router = DefaultRouter()
router.register(r'students', StudentView)
router.register(r'gaurdian', GuardianProfileViewSet)

# Combine the router's URL patterns with the admin URL pattern
urlpatterns = [
    path('', include(router.urls)),   # Router's URL patterns
]



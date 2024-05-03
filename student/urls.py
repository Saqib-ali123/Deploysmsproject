from django.urls import path
from .views import *


urlpatterns = [
    path("guardian-types/", GuardianTypeView, name="guardian-type"),
    path("guardian-type/<int:pk>/", GuardianTypeView, name="guardian-type-details"),
]
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from director.views import AddressView,PeriodView,CountryView,StateView,CityView
from django.contrib import admin

# Define the router for the StudentView
router = DefaultRouter()

router.register(r'country', CountryView)
router.register(r'states', StateView)
router.register(r'city', CityView)
router.register(r'addresses', AddressView)
router.register(r'Period', PeriodView)

# Combine the router's URL patterns with the admin URL pattern
urlpatterns = [
    path('admin/', admin.site.urls),  # Admin URL pattern
    path('', include(router.urls)),   # Router's URL patterns
]

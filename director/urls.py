from django.urls import path,include
from .views import *


urlpatterns = [
    path("year-levels/", YearLevelView),
    path("year-level/<int:id>/", YearLevelView),
    path("school-years/", SchoolYearView),
    path("school-year/<int:pk>/", SchoolYearView),
    path("departments/", DepartmentView),
    path("department/<int:pk>/", DepartmentView),
    path("classroom-types/", ClassRoomTypeView),
    path("classroom-type/<int:pk>/", ClassRoomTypeView),
    path("roles/", RoleView, name="roleDetails"),
    path("role/<int:pk>/", RoleView, name="roleDetails"),
]



from django.contrib import admin

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
router.register(r'terms', TermView)


# Combine the router's URL patterns with the admin URL pattern
urlpatterns = [
    path('admin/', admin.site.urls),  # Admin URL pattern
    path('', include(router.urls)),   # Router's URL patterns
]
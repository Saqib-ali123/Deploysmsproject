from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register(r'country', CountryView)
router.register(r'states', StateView)
router.register(r'city', CityView)
router.register(r'addresses', AddressView)
router.register(r'Period', PeriodView)
router.register(r'director', DirectorView)
router.register(r'banking_details', BankingDetailView)
router.register(r'terms', TermView)


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
    path('', include(router.urls)), 
]










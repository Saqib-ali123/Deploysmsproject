from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter



router = DefaultRouter()

router.register(r'country', CountryView)
router.register(r'states', StateView)
router.register(r'city', CityView)
router.register(r'addresses', AddressView)
router.register(r'Period', PeriodView)
router.register(r'classPeriod', ClassPeriodView)
router.register(r'director', DirectorView)
router.register(r'banking_details', BankingDetailView)
router.register(r'terms', TermView)
router.register(r'admission',AdmissionView)
router.register(r'officestaff',OfficeStaffView)
router.register(r'DocumentType',DocumentTypeView)
router.register(r'Document',DocumentView)
# router.register(r'class-periods', ClassPeriodView),
router.register(r'fee-types', FeeTypeView) # whole code commented as of 06June25 at 12:30 PM
router.register(r'year-level-fee', YearLevelFeeView)
router.register(r'fee-record', FeeRecordView, basename='fee-record') #
# router.register(r'submit_fee',FeeSubmitView, basename='submit_fee')


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
    # path('submit-fee/', FeeView.as_view(), name='submit-fee'),
    # path("fee_submission/<int:student_id>/", FeeSubmissionView.as_view(), name='fee-submission'),
]










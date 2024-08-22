from django.urls import path
from . import views
from django.contrib import admin
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView



urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", views.UserView, name="custom_user_list"),
    path("user/<int:pk>/", views.UserView, name="custom_user_detail"),
    path("change_password/", views.ChangePasswordView)
    path("login/", views.LoginViews),
    path("logout/", views.LogOutView),
    path('refreshtoken/',TokenRefreshView.as_view(),name='token_refresh'),
]

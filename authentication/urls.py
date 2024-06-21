from django.urls import path
from . import views
from django.contrib import admin


urlpatterns = [
    path("admin/", admin.site.urls),

    path("users/", views.UserView, name="custom_user_list"),
    path("user/<int:pk>/", views.UserView, name="custom_user_detail"),
    path("change_password/", views.ChangePasswordView)

]

from django.urls import path
from . import views

urlpatterns = [
    path("users/", views.UserView, name="custom_user_list"),
    path("user/<int:pk>/", views.UserView, name="custom_user_detail"),
    path("Login/", views.Login_Views),

]

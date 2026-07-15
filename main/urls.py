from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name=""),
    path("login-endpoint", views.login, name="login"),
    path("signup-endpoint", views.signup, name="signup")
]
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name=""),
    path("dashboard", views.dashboard, name="dashboard"),
    path("login-endpoint", views.login, name="login"),
    path("signup-endpoint", views.signup, name="signup"),
    path("logout", views.logout, name="logout")
]
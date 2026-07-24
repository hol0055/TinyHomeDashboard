from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name=""),
    path("dashboard", views.dashboard, name="dashboard"),
    path("loginEndpoint", views.login, name="login"),
    path("signupEndpoint", views.signup, name="signup"),
    path("logout", views.logout, name="logout"),
    path("filter", views.filter, name="filter"),
    path("sort", views.sort, name="sort"),
    path("setRanStart", views.setRanStart, name="setRanStart"),
    path("setRanEnd", views.setRanEnd, name="setRanEnd"),
    path("setFilter", views.setFilter, name="setFilter"),
    path("doRDDLogic", views.doRDDLogic, name="doRDDLogic"),
    path("doBreakdownLogic", views.doBreakdownLogic, name="doBreakdownLogic"),
    path("batteryStats", views.batteryStats, name="batteryStats"),
    path("insightLogic", views.insightLogic, name="insightLogic"),
    path("passwordReset", views.passwordReset, name="passwordReset")
]
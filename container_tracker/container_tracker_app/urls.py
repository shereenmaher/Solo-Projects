from django.urls import path
from . import views

urlpatterns = [
    path('', views.reg_log_page),
    path('dashboard', views.dashboard),
    path('login', views.login),
]
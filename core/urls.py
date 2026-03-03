# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('calendario/', views.calendario, name='calendario'),
    path('calendario/eventos/', views.calendario_eventos, name='calendario_eventos'),
]
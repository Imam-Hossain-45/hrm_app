from django.urls import path
from .views import DashboardView

app_name = 'dashboard'

urlpatterns = [
    path('api/dashboard/', DashboardView.as_view(), name='dashboard')
]

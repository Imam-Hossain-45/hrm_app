from django.urls import path, include
from . import views

app_name = 'beehive_admin'

urlpatterns = [
    path('leave/', include('leave.urls')),
    path('attendance/', include('attendance.urls')),
    path('payroll/', include('payroll.urls')),
    path('setting/', include('setting.urls')),
    path('report/', include('reporting.urls')),
]

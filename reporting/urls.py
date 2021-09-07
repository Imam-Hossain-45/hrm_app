from django.urls import path

from .views import LeaveReportView, BIRTDemoReportView

app_name = 'reporting'

urlpatterns = [
    path('leave/', LeaveReportView.as_view(), name='leave-report'),
    path('birt-demo/', BIRTDemoReportView.as_view(), name='birt-demo-report'),
]

from django.urls import path
from .views import *

app_name = 'self_panel'

urlpatterns = [
    path('attendance/remotely/', RemoteAttendanceView.as_view(), name='remote_attendance'),
    path('attendance/status/', AttendanceStatusView.as_view(), name='attendance_status'),

    path('leave/apply/', LeaveApplyView.as_view(), name='leave_apply'),
    path('leave/status/', LeaveStatusView.as_view(), name='leave_status'),
    path('leave/<pk>/edit/', LeaveApplyUpdateView.as_view(), name='leave_update'),
    path('leave/<pk>/delete/', LeaveDeleteView.as_view(), name='leave_delete'),

    path('late/status/', LateStatusListView.as_view(), name='late_status'),
    path('late/apply/', LateApplyView.as_view(), name='late_apply'),
    path('late/<pk>/edit/', LateUpdateView.as_view(), name='late_update'),
    path('late/<pk>/delete/', LateDeleteView.as_view(), name='late_delete'),

    path('early-out/status/', EarlyOutStatusListView.as_view(), name='early_out_status'),
    path('early-out/apply/', EarlyOutApplyView.as_view(), name='early_out_apply'),
    path('early-out/<pk>/edit/', EarlyOutUpdateView.as_view(), name='early_out_update'),
    path('early-out/<pk>/delete/', EarlyOutDeleteView.as_view(), name='early_out_delete'),
]

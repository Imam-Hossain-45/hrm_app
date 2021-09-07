from django.urls import path
import attendance.views as views
from leave.views import LeaveEntrySearchView

app_name = 'attendance'

# Update
master_calendar_urlpatterns = [
    path('master/calendar/', views.ListCalendarMasterView.as_view(), name='master_calendar_list'),
    path('master/calendar/create/', views.AddCalendarMasterView.as_view(), name='master_calendar_add'),
    path('master/calendar/<pk>/update/', views.EditCalendarMasterView.as_view(), name='master_calendar_update'),
    path('master/calendar/<pk>/delete/', views.DeleteCalendarMasterView.as_view(), name='master_calendar_delete'),
]

master_schedule_urlpatterns = [
    path('master/schedule/', views.ScheduleMasterListView.as_view(), name='master_schedule_list'),
    path('master/schedule/create/', views.ScheduleMasterCreateView.as_view(), name='master_schedule_create'),
    path('master/schedule/<pk>/update/', views.ScheduleMasterUpdateView.as_view(), name='master_schedule_update'),
    path('master/schedule<pk>/delete/', views.ScheduleMasterDeleteView.as_view(), name='master_schedule_delete'),
]

master_holiday_patterns = [
    path('master/holiday/create/', views.HolidayMasterCreate.as_view(), name='holiday_master_create'),
    path('master/holiday/', views.HolidayMasterList.as_view(), name='holiday_master_list'),
    path('master/holiday/<pk>/update/', views.HolidayMasterUpdate.as_view(), name='holiday_master_update'),
    path('master/holiday/<pk>/delete/', views.HolidayMasterDelete.as_view(), name='holiday_master_delete'),
]

master_holiday_group_patterns = [
    path('master/holiday-group/create/', views.HolidayGroupCreate.as_view(), name='holiday_group_create'),
    path('master/holiday-group/', views.HolidayGroupList.as_view(), name='holiday_group_list'),
    path('master/holiday-group/<pk>/update/', views.HolidayGroupUpdate.as_view(), name='holiday_group_update'),
    path('master/holiday-group/<pk>/delete/', views.HolidayGroupDelete.as_view(), name='holiday_group_delete'),
]

master_overtime_patterns = [
    path('master/overtime/', views.OvertimeMasterListView.as_view(), name='overtime_list'),
    path('master/overtime/create/', views.OvertimeMasterCreateView.as_view(), name='overtime_create'),
    path('master/overtime/<int:pk>/update/', views.OvertimeMasterUpdateView.as_view(), name='overtime_update'),
    path('master/overtime/<int:pk>/delete/', views.OvertimeMasterDeleteView.as_view(), name='overtime_delete'),
]

process_attendance_patterns = [
    path('process/manual_entry/', views.ManualAttendanceList.as_view(), name='manual_attendance_list'),
    path('process/manual_entry/leave_entry_search/', LeaveEntrySearchView.as_view(), name='entry_search_employee'),
    path('process/late_entry/', views.LateApplicationList.as_view(), name='late_entry_application_list'),
    path('process/late_entry/leave_entry_search/', LeaveEntrySearchView.as_view(), name='entry_search_employee'),
    path('process/late_entry/new/', views.LateEntryCreateView.as_view(), name='late_entry_new'),
    path('process/late_entry/new/leave_entry_search/', LeaveEntrySearchView.as_view(), name='entry_search_employee'),
    path('process/late_entry/new/get_entry_time/', views.EntryTimeView.as_view(), name='get_entry_time'),
    path('process/late_entry/list/?query=<pk>', views.LateIndividualListView.as_view(), name='late_entry_individual_list'),
    path('process/late_entry/<pk>/edit/?query=<employee_id>', views.LateEntryCreateView.as_view(), name='late_entry_new_edit'),
    path('process/late_entry/<pk>/details/?query=<employee_id>', views.LateEntryDetailsView.as_view(), name='late_entry_details'),
    path('process/late_entry_approval/list/', views.LatePendingListView.as_view(), name='late_approval_list'),
    path('process/late_entry_approval/list/leave_entry_search/',LeaveEntrySearchView.as_view(), name='entry_search_employee'),
    path('process/late_entry_approval/<pk>/', views.LateApprovalView.as_view(), name='late_approval_form'),
    path('process/early_out/', views.EarlyApplicationList.as_view(), name='early_out_application_list'),
    path('process/early_out/leave_entry_search/', LeaveEntrySearchView.as_view(), name='entry_search_employee'),
    path('process/early_out/new/', views.EarlyOutCreateView.as_view(), name='early_out_new'),
    path('process/early_out/new/leave_entry_search/', LeaveEntrySearchView.as_view(), name='entry_search_employee'),
    path('process/early_out/new/get_out_time/', views.OutTimeView.as_view(), name='get_out_time'),
    path('process/early_out/list/?query=<pk>', views.EarlyOutIndividualListView.as_view(), name='early_out_individual_list'),
    path('process/early_out/<pk>/edit/?query=<employee_id>', views.EarlyOutCreateView.as_view(), name='early_out_new_edit'),
    path('process/early_out/<pk>/details/?query=<employee_id>', views.EarlyOutDetailsView.as_view(), name='early_out_details'),
    path('process/early_out_approval/list/', views.EarlyPendingListView.as_view(), name='early_approval_list'),
    path('process/early_out_approval/list/leave_entry_search/', LeaveEntrySearchView.as_view(), name='entry_search_employee'),
    path('process/early_out_approval/<pk>/', views.EarlyApprovalView.as_view(), name='early_approval_form'),
    path('process/upload_attendance/', views.UploadAttendanceView.as_view(), name='upload_attendance'),
]

attendance_scheduling_patterns = [
    path('scheduling/', views.SchedulerRecordView.as_view(), name='attendance_scheduling'),
    path('scheduling/leave_entry_search/', LeaveEntrySearchView.as_view(), name='entry_search_employee'),
]

attendance_report_patterns = [
    path('report/', views.AttendanceReportView.as_view(), name='attendance_report'),
    path('report/leave_entry_search/', LeaveEntrySearchView.as_view(), name='leave_entry_search'),
]

urlpatterns = (master_calendar_urlpatterns + master_schedule_urlpatterns + master_holiday_patterns
               + master_holiday_group_patterns + master_overtime_patterns + process_attendance_patterns +
               attendance_scheduling_patterns + attendance_report_patterns)

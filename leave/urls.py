from django.urls import path
from .views import *

app_name = 'leave'

master_leave_patterns = [
    path('master/creation/', LeaveMasterListView.as_view(), name='leave_master_list'),
    path('master/creation/create/', LeaveMasterCreateView.as_view(), name='leave_master_create'),
    path('master/creation/<pk>/update/', LeaveMasterUpdateView.as_view(), name='leave_master_edit'),
    path('master/creation/<pk>/delete/', LeaveDeleteView.as_view(), name='leave_master_delete'),
]

master_leave_group_patterns = [
    path('master/group/', LeaveGroupListView.as_view(), name='leave_group_list'),
    path('master/group/create/', LeaveGroupCreateView.as_view(), name='leave_group_create'),
    path('master/group/<pk>/update/', LeaveGroupUpdateView.as_view(), name='leave_group_edit'),
    path('master/group/<pk>/delete/', LeaveGroupDeleteView.as_view(), name='leave_group_delete'),
]

process_leave_patterns = [
    path('process/entry/', LeaveEntryListView.as_view(), name='leave_entry_list'),
    path('process/entry/new/', LeaveEntryCreateView.as_view(), name='leave_entry_new'),
    path('process/entry/new/<pk>/edit/?query=<employee_id>', LeaveEntryCreateView.as_view(), name='leave_entry_new_edit'),
    path('process/entry/<pk>/details/?query=<employee_id>', LeaveEntryDetailsView.as_view(), name='leave_entry_details'),
    path('process/entry/list/?query=<pk>', LeaveIndividualListView.as_view(), name='leave_entry_individual_list'),
    path('process/entry/new/leave_entry_search/', LeaveEntrySearchView.as_view(), name='leave_entry_search'),
    path('process/entry/leave_entry_search/', LeaveEntrySearchView.as_view(), name='entry_search_employee'),
    path('process/leave_approval/list/', LeavePendingListView.as_view(), name='leave_approval_list'),
    path('process/leave_approval/<pk>/', LeaveApprovalView.as_view(), name='leave_approval_form'),
    path('process/leave_approval/list/leave_entry_search/', LeaveEntrySearchView.as_view(), name='leave_entry_search'),
]

leave_report_patterns = [
    path('report/', LeaveReportView.as_view(), name='leave_report'),
    path('report/leave_entry_search/', LeaveEntrySearchView.as_view(), name='leave_entry_search'),
]

urlpatterns = master_leave_patterns + master_leave_group_patterns + process_leave_patterns + leave_report_patterns

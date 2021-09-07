from django.urls import path
from employees import views

app_name = 'subordinate'

urlpatterns = [
    path('list/pending', views.LeaveApplicationSubordinateListView.as_view(),
         name='subordinate_pending_leave_application_list'),
    path('list/accepted', views.LeaveApplicationAcceptedSubordinateListView.as_view(),
         name='subordinate_accepted_leave_application_list'),
    path('list/declined', views.LeaveApplicationDeclinedSubordinateListView.as_view(),
         name='subordinate_declined_leave_application_list'),
    path('detail/<pk>', views.LeaveApplicationSubordinateDetailView.as_view(),
         name='subordinate_leave_application_detail'),
]

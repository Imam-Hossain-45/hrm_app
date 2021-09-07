from django.urls import path
from employees import views

app_name = 'employees'

master_employee_patterns = [
    path('master/', views.EmployeeListView.as_view(),
         name='employee_master_list'),
    path('master/create/', views.EmployeeIdentificationCreateView.as_view(),
         name='employee_identification_create'),
    path('master/<pk>/delete/', views.EmployeeDeleteView.as_view(),
         name='employee_master_delete'),
    path('master/<pk>/update/', views.EmployeeIdentificationUpdateView.as_view(),
         name='employee_identification_update'),
    path('master/<pk>/job/list/', views.EmployeeJobListView.as_view(),
         name='employee_job_list'),
    path('master/<pk>/job/create/', views.EmployeeJobCreateView.as_view(),
         name='employee_job_create'),
    path('master/<pk>/job/<job_id>/update/', views.EmployeeJobUpdateView.as_view(),
         name='employee_job_update'),
    path('master/<employee_pk>/job/<pk>/delete/', views.EmployeeJobDeleteView.as_view(),
         name='employee_job_delete'),
    path('master/<pk>/attendance_&_leave/', views.LeaveManagerCreateView.as_view(),
         name='employee_attendance_leave'),
]
master_employee_info_patterns = [
    path('master/<pk>/personal_info/', views.EmployeePersonalCreateView.as_view(),
         name='employee_personal_info'),
    path('master/<pk>/address_&_contact/', views.EmployeeContactCreateView.as_view(),
         name='employee_contact_info'),
    path('master/<pk>/family/', views.EmployeeFamilyCreateView.as_view(),
         name='employee_family_info'),
    path('master/<pk>/previous_employment/', views.EmploymentHistoryCreateView.as_view(),
         name='employment_history'),
    path('master/<pk>/reference/', views.ReferenceCreateView.as_view(),
         name='employee_reference_create'),
    path('master/<pk>/reference/list/', views.ReferenceListView.as_view(),
         name='employee_reference_list'),
    path('master/<pk>/reference/<reference_id>/update/', views.ReferenceCreateView.as_view(),
         name='employee_reference_update'),
    path('master/<employee_pk>/reference/<pk>/delete/', views.ReferenceDeleteView.as_view(),
         name='employee_reference_delete'),
    path('master/<pk>/asset/', views.AssetCreateView.as_view(),
         name='employee_asset_create'),
    path('master/<pk>/asset/list/', views.AssetListView.as_view(),
         name='employee_asset_list'),
    path('master/<pk>/asset/<asset_id>/update/', views.AssetCreateView.as_view(),
         name='employee_asset_update'),
    path('master/<employee_pk>/asset/<pk>/delete/', views.AssetDeleteView.as_view(),
         name='employee_asset_delete'),
    path('master/<pk>/document/', views.DocumentView.as_view(),
         name='employee_document'),
]
master_employee_qualification_patterns = [
    path('master/<pk>/education/', views.EducationCreateView.as_view(),
         name='employee_education_create'),
    path('master/<pk>/education/list/', views.EducationListView.as_view(),
         name='employee_education_list'),
    path('master/<pk>/education/<education_id>/update/', views.EducationCreateView.as_view(),
         name='employee_education_update'),
    path('master/<employee_pk>/education/<pk>/delete/', views.EducationDeleteView.as_view(),
         name='employee_education_delete'),
    path('master/<pk>/skill_training_language/', views.EmployeeSkillCreateView.as_view(),
         name='employee_skill_info'),
]

master_employee_salary_patterns = [
    path('master/<pk>/salary/', views.EmployeeSalaryCreateView.as_view(), name='employee_salary_create'),
    path('master/<pk>/salary/list/', views.EmployeeSalaryListView.as_view(), name='employee_salary_list'),
    path('master/<employee_id>/salary/<pk>/delete/', views.EmployeeSalaryDeleteView.as_view(),
         name='employee_salary_structure_delete'),
    path('master/<employee_id>/salary/<pk>/edit/', views.EmployeeSalaryUpdateView.as_view(),
         name='employee_salary_structure_edit'),
]

urlpatterns = master_employee_patterns + master_employee_info_patterns + master_employee_qualification_patterns + master_employee_salary_patterns

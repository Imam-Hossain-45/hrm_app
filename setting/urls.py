from django.urls import path

from . import views

app_name = 'setting'

urlpatterns = [
    path(
        'organization/organizational-structure/', views.OrganizationalStructureList.as_view(),
        name='organizational_structure_list'
    ),
    path(
        'organization/organizational-structure/create/', views.OrganizationalStructureCreate.as_view(),
        name='organizational_structure_create'
    ),
    path(
        'organization/organizational-structure/<int:pk>/update/', views.OrganizationalStructureUpdate.as_view(),
        name='organizational_structure_update'
    ),
    path(
        'organization/organizational-structure/<int:pk>/delete/', views.OrganizationalStructureDelete.as_view(),
        name='organizational_structure_delete'
    ),

    path('industry/', views.IndustryList.as_view(), name='industry_list'),
    path('industry/create/', views.IndustryCreate.as_view(), name='industry_create'),
    path('industry/<int:pk>/update/', views.IndustryUpdate.as_view(), name='industry_update'),
    path('industry/<int:pk>/delete/', views.IndustryDelete.as_view(), name='industry_delete'),

    path('organization/company/', views.CompanyList.as_view(), name='company_list'),
    path('organization/company/create/', views.CompanyCreate.as_view(), name='company_create'),
    path('organization/company/<int:pk>/update/', views.CompanyUpdate.as_view(), name='company_update'),
    path('organization/company/<int:pk>/delete/', views.CompanyDelete.as_view(), name='company_delete'),

    path('organization/branch/', views.BranchList.as_view(), name='branch_list'),
    path('organization/branch/create/', views.BranchCreate.as_view(), name='branch_create'),
    path('organization/branch/<int:pk>/update/', views.BranchUpdate.as_view(), name='branch_update'),
    path('organization/branch/<int:pk>/delete/', views.BranchDelete.as_view(), name='branch_delete'),

    path('organization/business-units/', views.BusinessUnitList.as_view(), name='business_unit_list'),
    path('organization/business-units/create/', views.BusinessUnitCreate.as_view(), name='business_unit_create'),
    path('organization/business-units/<int:pk>/update/', views.BusinessUnitUpdate.as_view(), name='business_unit_update'),
    path('organization/business-units/<int:pk>/delete/', views.BusinessUnitDelete.as_view(), name='business_unit_delete'),

    path('organization/divisions/', views.DivisionList.as_view(), name='division_list'),
    path('organization/divisions/create/', views.DivisionCreate.as_view(), name='division_create'),
    path('organization/divisions/<int:pk>/update/', views.DivisionUpdate.as_view(), name='division_update'),
    path('organization/divisions/<int:pk>/delete/', views.DivisionDelete.as_view(), name='division_delete'),

    path('organization/departments/', views.DepartmentList.as_view(), name='department_list'),
    path('organization/departments/create/', views.DepartmentCreate.as_view(), name='department_create'),
    path('organization/departments/<int:pk>/update/', views.DepartmentUpdate.as_view(), name='department_update'),
    path('organization/departments/<int:pk>/delete/', views.DepartmentDelete.as_view(), name='department_delete'),

    path('organization/projects/', views.ProjectList.as_view(), name='project_list'),
    path('organization/projects/create/', views.ProjectCreate.as_view(), name='project_create'),
    path('organization/projects/<int:pk>/update/', views.ProjectUpdate.as_view(), name='project_update'),
    path('organization/projects/<int:pk>/delete/', views.ProjectDelete.as_view(), name='project_delete'),

    path('organization/designations/', views.DesignationList.as_view(), name='designation_list'),
    path('organization/designations/create/', views.DesignationCreate.as_view(), name='designation_create'),
    path('organization/designations/<int:pk>/update/', views.DesignationUpdate.as_view(), name='designation_update'),
    path('organization/designations/<int:pk>/delete/', views.DesignationDelete.as_view(), name='designation_delete'),

    path('api/get_identification_json', views.GetIdentificationJson.as_view(), name='get_identification_json')
]

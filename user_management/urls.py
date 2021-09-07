from django.urls import path
from .views import (
    RoleCreationListView, RoleCreationCreateView, RoleCreationUpdateView, RoleCreationDeleteView,
    UserCreationListView, UserCreationCreateView, UserCreationUpdateView, UserCreationDeleteView, ResetPasswordView,
    RoleHierarchyListView, RoleHierarchyCreateView, RoleHierarchyUpdateView, RoleHierarchyDeleteView,
    WorkflowListView, WorkflowCreateView, WorkflowUpdateView, WorkflowDeleteView,
)

app_name = 'user_management'

urlpatterns = [
    path('roles/', RoleCreationListView.as_view(), name='roles_list'),
    path('roles/create/', RoleCreationCreateView.as_view(), name='roles_create'),
    path('roles/<pk>/update/', RoleCreationUpdateView.as_view(), name='roles_update'),
    path('roles/<pk>/delete/', RoleCreationDeleteView.as_view(), name='roles_delete'),

    # User creation
    path('users/', UserCreationListView.as_view(), name='users_list'),
    path('users/create/', UserCreationCreateView.as_view(), name='users_create'),
    path('users/<pk>/update/', UserCreationUpdateView.as_view(), name='users_update'),
    path('users/<pk>/password-reset/', ResetPasswordView.as_view(), name='users_password_reset'),
    path('users/<pk>/delete/', UserCreationDeleteView.as_view(), name='users_delete'),

    # Role hierarchy
    path('role_hierarchies/', RoleHierarchyListView.as_view(), name='role_hierarchies_list'),
    path('role_hierarchies/create/', RoleHierarchyCreateView.as_view(), name='role_hierarchies_create'),
    path('role_hierarchies/<pk>/update/', RoleHierarchyUpdateView.as_view(), name='role_hierarchies_update'),
    path('role_hierarchies/<pk>/delete/', RoleHierarchyDeleteView.as_view(), name='role_hierarchies_delete'),

    # Workflow
    path('workflows/', WorkflowListView.as_view(), name='workflows_list'),
    path('workflows/<id>/define/', WorkflowCreateView.as_view(), name='workflows_create'),
    path('workflows/<content_id>/update/<pk>/', WorkflowUpdateView.as_view(), name='workflows_update'),
    path('workflows/<content_id>/delete/<pk>/', WorkflowDeleteView.as_view(), name='workflows_delete'),
]

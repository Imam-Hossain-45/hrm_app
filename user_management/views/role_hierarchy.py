from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from helpers.mixins import PermissionMixin
from user_management.models import RoleHierarchy
from helpers.functions import get_organizational_structure


class RoleHierarchyListView(ListView, PermissionMixin, LoginRequiredMixin):
    """List of role hierarchies."""

    template_name = 'user_management/role_hierarchy/list.html'
    model = RoleHierarchy
    context_object_name = 'role_hierarchies'
    permission_required = ['add_rolehierarchy', 'change_rolehierarchy', 'delete_rolehierarchy', 'view_rolehierarchy']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context


class RoleHierarchyCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    """Show the form to create and store the newly created hierarchy."""

    template_name = 'user_management/role_hierarchy/create.html'
    model = RoleHierarchy
    fields = '__all__'
    success_url = reverse_lazy('user_management:role_hierarchies_list')
    permission_required = 'add_rolehierarchy'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context


class RoleHierarchyUpdateView(LoginRequiredMixin, PermissionMixin, UpdateView):
    """Show the form to update the specified hierarchy."""

    template_name = 'user_management/role_hierarchy/update.html'
    model = RoleHierarchy
    fields = '__all__'
    success_url = reverse_lazy('user_management:role_hierarchies_list')
    permission_required = 'change_rolehierarchy'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context


class RoleHierarchyDeleteView(LoginRequiredMixin, PermissionMixin, DeleteView):
    """Delete the specified role."""

    template_name = 'user_management/role_hierarchy/delete.html'
    model = RoleHierarchy
    success_url = reverse_lazy('user_management:role_hierarchies_list')
    permission_required = 'delete_rolehierarchy'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

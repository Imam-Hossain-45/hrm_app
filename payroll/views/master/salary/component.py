from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from helpers.mixins import PermissionMixin
from payroll.models import Component
from helpers.functions import get_organizational_structure


class PayrollComponentList(LoginRequiredMixin, PermissionMixin, ListView):
    """Show the list of all salary components."""

    template_name = 'payroll/component/list.html'
    model = Component
    context_object_name = 'components'
    permission_required = ['view_component', 'add_component', 'change_component', 'delete_component']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        paginator = Paginator(self.object_list, 50)
        page = self.request.GET.get('page')
        context['components'] = paginator.get_page(page)
        index = context['components'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class PayrollComponentCreate(LoginRequiredMixin, PermissionMixin, CreateView):
    """Handle salary create component request."""

    template_name = 'payroll/component/create.html'
    model = Component
    fields = ('name', 'short_code', 'description', 'status', 'component_type', 'is_gross', 'is_taxable')
    permission_required = 'add_component'
    success_url = reverse_lazy('beehive_admin:payroll:component_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context


class PayrollComponentUpdate(LoginRequiredMixin, PermissionMixin, UpdateView):
    """Handle update salary component request."""

    template_name = 'payroll/component/update.html'
    model = Component
    fields = ('name', 'short_code', 'description', 'status', 'component_type', 'is_gross', 'is_taxable')
    permission_required = 'change_component'
    success_url = reverse_lazy('beehive_admin:payroll:component_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context


class PayrollComponentDelete(LoginRequiredMixin, PermissionMixin, DeleteView):
    """Handle delete salary component request."""

    model = Component
    context_object_name = 'component'
    permission_required = 'delete_component'
    success_url = reverse_lazy('beehive_admin:payroll:component_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

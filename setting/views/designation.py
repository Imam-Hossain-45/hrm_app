from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from helpers.mixins import PermissionMixin
from setting.models import Designation
from helpers.functions import get_organizational_structure


class DesignationList(LoginRequiredMixin, PermissionMixin, ListView):
    """Show the list of all designations."""

    template_name = 'setting/designation/list.html'
    model = Designation
    context_object_name = 'designations'
    permission_required = ['view_designation', 'add_designation', 'change_designation', 'delete_designation']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        paginator = Paginator(self.object_list, 50)
        page = self.request.GET.get('page')
        context['designations'] = paginator.get_page(page)
        index = context['designations'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class DesignationCreate(LoginRequiredMixin, PermissionMixin, CreateView):
    """create designation request."""

    template_name = 'setting/designation/create.html'
    model = Designation
    fields = ('name', 'short_code', 'description', 'status')
    permission_required = 'add_designation'
    success_url = reverse_lazy('beehive_admin:setting:designation_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context


class DesignationUpdate(LoginRequiredMixin, PermissionMixin, UpdateView):
    """ Update a selected designation """

    template_name = 'setting/designation/update.html'
    model = Designation
    fields = ('name', 'short_code', 'description', 'status')
    permission_required = 'change_designation'
    success_url = reverse_lazy('beehive_admin:setting:designation_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context


class DesignationDelete(LoginRequiredMixin, PermissionMixin, DeleteView):
    """ Delete a selected designation    """

    model = Designation
    context_object_name = 'designation'
    permission_required = 'delete_designation'
    success_url = reverse_lazy('beehive_admin:setting:designation_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

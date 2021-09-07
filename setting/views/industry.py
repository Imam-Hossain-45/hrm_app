from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from helpers.mixins import PermissionMixin
from setting.models import Industry
from helpers.functions import get_organizational_structure


class IndustryList(LoginRequiredMixin, PermissionMixin, ListView):
    permission_required = ['add_industry', 'update_industry', 'view_industry', 'delete_industry']
    template_name = 'setting/industry/list.html'
    model = Industry
    context_object_name = 'industries'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        paginator = Paginator(self.object_list, 50)
        page = self.request.GET.get('page')
        context['industries'] = paginator.get_page(page)
        index = context['industries'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class IndustryCreate(LoginRequiredMixin, PermissionMixin, CreateView):
    permission_required = 'add_industry'
    template_name = 'setting/industry/create.html'
    model = Industry
    fields = '__all__'
    success_url = reverse_lazy('beehive_admin:setting:industry_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context


class IndustryUpdate(LoginRequiredMixin, PermissionMixin, UpdateView):
    permission_required = 'update_industry'
    template_name = 'setting/industry/update.html'
    model = Industry
    fields = '__all__'
    success_url = reverse_lazy('beehive_admin:setting:industry_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context


class IndustryDelete(LoginRequiredMixin, PermissionMixin, DeleteView):
    permission_required = 'delete_industry'
    model = Industry
    success_url = reverse_lazy('beehive_admin:setting:industry_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

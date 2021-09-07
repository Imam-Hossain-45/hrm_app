from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from helpers.mixins import PermissionMixin
from payroll.models import BonusComponent
from helpers.functions import get_organizational_structure


class BonusComponentList(LoginRequiredMixin, PermissionMixin, ListView):
    """Show the list of all bonus components."""

    template_name = 'payroll/master/bonus_component/list.html'
    model = BonusComponent
    context_object_name = 'bonus_components'
    permission_required = ['view_bonuscomponent', 'add_bonuscomponent', 'change_bonuscomponent',
                           'delete_bonuscomponent']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        paginator = Paginator(self.object_list, 50)
        page = self.request.GET.get('page')
        context['bonus_components'] = paginator.get_page(page)
        index = context['bonus_components'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class BonusComponentCreate(LoginRequiredMixin, PermissionMixin, CreateView):
    """create bonus component request."""

    template_name = 'payroll/master/bonus_component/create.html'
    model = BonusComponent
    fields = ('name', 'short_code', 'description', 'status')
    permission_required = 'add_bonuscomponent'
    success_url = reverse_lazy('beehive_admin:payroll:bonus_component_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context


class BonusComponentUpdate(LoginRequiredMixin, PermissionMixin, UpdateView):
    """ Update a selected bonus component """

    template_name = 'payroll/master/bonus_component/update.html'
    model = BonusComponent
    fields = ('name', 'short_code', 'description', 'status')
    permission_required = 'change_bonuscomponent'
    success_url = reverse_lazy('beehive_admin:payroll:bonus_component_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['component'] = BonusComponent.objects.get(id=self.kwargs.get('pk', ''))
        return context


class BonusComponentDelete(LoginRequiredMixin, PermissionMixin, DeleteView):
    """ Delete a selected bonus component    """

    model = BonusComponent
    context_object_name = 'bonus_component'
    permission_required = 'delete_bonuscomponent'
    success_url = reverse_lazy('beehive_admin:payroll:bonus_component_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

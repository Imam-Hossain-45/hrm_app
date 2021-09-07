from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from helpers.mixins import PermissionMixin
from payroll.models import DeductionComponent
from django.shortcuts import redirect, render
from helpers.functions import get_organizational_structure


class DeductionComponentList(LoginRequiredMixin, PermissionMixin, ListView):
    """Show the list of all deduction components."""

    template_name = 'payroll/master/deduction/deduction_component/list.html'
    model = DeductionComponent
    context_object_name = 'deduction_components'
    permission_required = ['view_deductioncomponent', 'add_deductioncomponent', 'change_deductioncomponent',
                           'delete_deductioncomponent']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        paginator = Paginator(self.object_list, 50)
        page = self.request.GET.get('page')
        context['deduction_components'] = paginator.get_page(page)
        index = context['deduction_components'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class DeductionComponentCreate(LoginRequiredMixin, PermissionMixin, CreateView):
    """create deduction component request."""

    template_name = 'payroll/master/deduction/deduction_component/create.html'
    model = DeductionComponent
    fields = ('name', 'short_code', 'description', 'status', 'deduction_component_type')
    permission_required = 'add_deductioncomponent'
    success_url = reverse_lazy('beehive_admin:payroll:deduction_component_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def post(self, request, *args, **kwargs):
        submitted_form = self.get_form()
        if not submitted_form.is_valid():
            return render(request, self.template_name, {'permissions': self.get_current_user_permission_list(),
                                                        'org_items_list': get_organizational_structure(),
                                                        'form': submitted_form})

        component = submitted_form.save(commit=False)
        component.save()

        return redirect(self.success_url)


class DeductionComponentUpdate(LoginRequiredMixin, PermissionMixin, UpdateView):
    """ Update a selected deduction component """

    template_name = 'payroll/master/deduction/deduction_component/update.html'
    model = DeductionComponent
    fields = ('name', 'short_code', 'description', 'status', 'deduction_component_type')
    permission_required = 'change_deductioncomponent'
    success_url = reverse_lazy('beehive_admin:payroll:deduction_component_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['component'] = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context


class DeductionComponentDelete(LoginRequiredMixin, PermissionMixin, DeleteView):
    """ Delete a selected deduction component    """

    model = DeductionComponent
    context_object_name = 'deduction_component'
    permission_required = 'delete_deductioncomponent'
    success_url = reverse_lazy('beehive_admin:payroll:deduction_component_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

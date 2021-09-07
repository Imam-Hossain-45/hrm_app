from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, DeleteView, FormView
from payroll.forms import DeductionGroupCreateForm
from payroll.models import DeductionGroup, DeductionComponent
from helpers.mixins import PermissionMixin
from django.contrib import messages
from helpers.functions import get_organizational_structure


class DeductionGroupList(LoginRequiredMixin, PermissionMixin, ListView):
    """
        List of Deduction Group
    """

    model = DeductionGroup
    context_object_name = 'groups'
    template_name = "payroll/master/deduction/deduction_group/list.html"
    permission_required = ['add_deductiongroup', 'change_deductiongroup', 'view_deductiongroup',
                           'delete_deductiongroup']

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        paginator = Paginator(self.object_list, 50)
        page = self.request.GET.get('page')
        context['groups'] = paginator.get_page(page)
        index = context['groups'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class DeductionGroupCreate(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Create new Deduction Group
    """

    template_name = 'payroll/master/deduction/deduction_group/create.html'
    permission_required = 'add_deductiongroup'

    def get(self, request, *args, **kwargs):
        context = {
            'form': DeductionGroupCreateForm(),
            'permissions': self.get_current_user_permission_list(),
            'org_items_list': get_organizational_structure(),
            'selected_absent_component': 'None',
            'selected_late_component': 'None',
            'selected_early_out_component': 'None',
            'selected_under_work_component': 'None',
            'selected_other_component': 'None'
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = DeductionGroupCreateForm(request.POST)

        selected_absent_component = request.POST.get('absent_component_options')
        selected_late_component = request.POST.get('late_component_options')
        selected_early_out_component = request.POST.get('early_out_component_options')
        selected_under_work_component = request.POST.get('under_work_component_options')
        selected_other_component = request.POST.get('other_component_options')

        if not form.is_valid():
            return render(request, self.template_name, {
                'permissions': self.get_current_user_permission_list(),
                'org_items_list': get_organizational_structure(),
                'form': form,
                'selected_absent_component':
                    int(selected_absent_component) if not selected_absent_component == 'None' else 'None',
                'selected_late_component':
                    int(selected_late_component) if not selected_late_component == 'None' else 'None',
                'selected_early_out_component':
                    int(selected_early_out_component) if not selected_early_out_component == 'None' else 'None',
                'selected_under_work_component':
                    int(selected_under_work_component) if not selected_under_work_component == 'None' else 'None',
                'selected_other_component':
                    int(selected_other_component) if not selected_other_component == 'None' else 'None'
            })

        group = form.save(commit=False)
        if selected_absent_component == 'None':
            group.absent_component = None
        else:
            group.absent_component = DeductionComponent.objects.get(id=int(selected_absent_component))
        if selected_late_component == 'None':
            group.late_component = None
        else:
            group.late_component = DeductionComponent.objects.get(id=int(selected_late_component))
        if selected_early_out_component == 'None':
            group.early_out_component = None
        else:
            group.early_out_component = DeductionComponent.objects.get(id=int(selected_early_out_component))
        if selected_under_work_component == 'None':
            group.under_work_component = None
        else:
            group.under_work_component = DeductionComponent.objects.get(id=int(selected_under_work_component))
        if selected_other_component == 'None':
            group.other_component = None
        else:
            group.other_component = DeductionComponent.objects.get(id=int(selected_other_component))

        group.save()
        messages.success(request, f'{group} was created successfully')
        return redirect(reverse_lazy('beehive_admin:payroll:deduction_group_list'))


class DeductionGroupUpdate(LoginRequiredMixin, PermissionMixin, FormView):
    """
        Change Deduction Group
    """

    form_class = DeductionGroupCreateForm
    template_name = "payroll/master/deduction/deduction_group/update.html"
    permission_required = 'change_deductiongroup'

    def get_object(self, queryset=None):
        group = DeductionGroup.objects.get(id=self.kwargs.get('pk', ''))
        return get_object_or_404(DeductionGroup, pk=group.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = DeductionGroup.objects.get(id=self.kwargs.get('pk', ''))
        initial = {
            'name': group.name,
            'short_code': group.short_code,
            'description': group.description,
            'status': group.status,
        }
        context['form'] = self.form_class(initial=initial)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['selected_absent_component'] = \
            group.absent_component.id if not group.absent_component is None else 'None'
        context['selected_late_component'] = \
            group.late_component.id if not group.late_component is None else 'None'
        context['selected_early_out_component'] = \
            group.early_out_component.id if not group.early_out_component is None else 'None'
        context['selected_under_work_component'] = \
            group.under_work_component.id if not group.under_work_component is None else 'None'
        context['selected_other_component'] = \
            group.other_component.id if not group.other_component is None else 'None'
        return context

    def post(self, request, *args, **kwargs):
        form = DeductionGroupCreateForm(request.POST)

        selected_absent_component = request.POST.get('absent_component_options')
        selected_late_component = request.POST.get('late_component_options')
        selected_early_out_component = request.POST.get('early_out_component_options')
        selected_under_work_component = request.POST.get('under_work_component_options')
        selected_other_component = request.POST.get('other_component_options')

        if not form.my_is_valid():
            return render(request, self.template_name, {
                'permissions': self.get_current_user_permission_list(),
                'org_items_list': get_organizational_structure(),
                'form': form,
                'selected_absent_component':
                    int(selected_absent_component) if not selected_absent_component == 'None' else 'None',
                'selected_late_component':
                    int(selected_late_component) if not selected_late_component == 'None' else 'None',
                'selected_early_out_component':
                    int(selected_early_out_component) if not selected_early_out_component == 'None' else 'None',
                'selected_under_work_component':
                    int(selected_under_work_component) if not selected_under_work_component == 'None' else 'None',
                'selected_other_component':
                    int(selected_other_component) if not selected_other_component == 'None' else 'None'
            })

        group = DeductionGroup.objects.get(id=self.get_object().id)

        group.name = form.cleaned_data['name']
        group.short_code = form.cleaned_data['short_code']
        group.description = form.cleaned_data['description']
        group.status = form.cleaned_data['status']

        if selected_absent_component == 'None':
            group.absent_component = None
        else:
            group.absent_component = DeductionComponent.objects.get(id=int(selected_absent_component))
        if selected_late_component == 'None':
            group.late_component = None
        else:
            group.late_component = DeductionComponent.objects.get(id=int(selected_late_component))
        if selected_early_out_component == 'None':
            group.early_out_component = None
        else:
            group.early_out_component = DeductionComponent.objects.get(id=int(selected_early_out_component))
        if selected_under_work_component == 'None':
            group.under_work_component = None
        else:
            group.under_work_component = DeductionComponent.objects.get(id=int(selected_under_work_component))
        if selected_other_component == 'None':
            group.other_component = None
        else:
            group.other_component = DeductionComponent.objects.get(id=int(selected_other_component))

        group.save()
        messages.success(request, f'{group} was updated successfully')
        return redirect(reverse_lazy('beehive_admin:payroll:deduction_group_list'))


class DeductionGroupDelete(LoginRequiredMixin, PermissionMixin, DeleteView):
    """
            Delete Deduction group
        """

    model = DeductionGroup
    success_message = "%(name)s deleted."
    context_object_name = 'deduction_group'
    success_url = reverse_lazy("beehive_admin:payroll:deduction_group_list")
    permission_required = 'delete_deductiongroup'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(DeductionGroupDelete, self).delete(request, *args, **kwargs)

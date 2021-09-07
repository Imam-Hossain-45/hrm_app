from django.views.generic import ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from helpers.mixins import PermissionMixin
from django.contrib import messages
from payroll.models import SalaryGroupComponent, Component, SalaryGroup
from payroll.forms import SalaryGroupSettingsUpdateForm
from django.shortcuts import render, Http404
from django.forms import inlineformset_factory
from cimbolic.models import Formula, Variable
from helpers.functions import get_organizational_structure


class SalaryGroupSettingsList(LoginRequiredMixin, PermissionMixin, ListView):
    """
        List of Salary Group members
    """

    model = SalaryGroupComponent
    template_name = "payroll/salary_group/settings/list.html"
    permission_required = ['add_salarygroup', 'change_salarygroup', 'view_salarygroup', 'delete_salarygroup',
                           'view_salarygroupcomponent', 'change_salarygroupcomponent']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        salary_group = SalaryGroup.objects.get(id=self.kwargs.get('pk', ''))
        context['salary_group'] = salary_group
        context['list_view'] = 'selected'
        context['components'] = Component.objects.filter(salarygroupcomponent__salary_group=salary_group)
        return context


class SalaryGroupSettingsUpdate(LoginRequiredMixin, PermissionMixin, FormView):
    """
        Update a Salary Group member
    """

    form_class = SalaryGroupSettingsUpdateForm
    template_name = "payroll/salary_group/settings/list.html"
    permission_required = ['change_salarygroup', 'change_salarygroupcomponent']

    rule_based_formset_class = inlineformset_factory(
        Variable,
        Formula,
        fields=['variable', 'priority', 'condition', 'rule'],
        extra=0,
        min_num=1,
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['update_component'] = 'Selected'
        salary_group = SalaryGroup.objects.get(id=self.kwargs.get('pk', ''))
        selected_component = Component.objects.get(id=self.kwargs.get('pk2', ''))
        context['salary_group'] = salary_group
        context['selected_component'] = selected_component
        context['form'] = self.form_class()
        context['components'] = Component.objects.filter(salarygroupcomponent__salary_group=salary_group)
        group_component_object = SalaryGroupComponent.objects.get(salary_group=salary_group,
                                                                  component=selected_component)
        context['selected_item'] = group_component_object.condition_type
        if context['selected_item'] == 'mapped':
            context['selected_mapped_item'] = group_component_object.mapping_policy
        try:
            salary_group_component = SalaryGroupComponent.objects.get(
                salary_group=salary_group,
                component=selected_component,
            )
        except SalaryGroupComponent.DoesNotExist as e:
            raise Http404('Salary group component does not exist') from e
        context['salary_group_component'] = salary_group_component
        context['rbforms'] = self.rule_based_formset_class(
            instance=salary_group_component.variable,
        )
        return context

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['update_component'] = 'Selected'
        form = SalaryGroupSettingsUpdateForm(request.POST)
        context['form'] = form
        selected_item = request.POST.get('options')
        context['selected_item'] = selected_item
        salary_group = SalaryGroup.objects.get(id=self.kwargs.get('pk', ''))
        selected_component = Component.objects.get(id=self.kwargs.get('pk2', ''))
        context['salary_group'] = salary_group
        context['selected_component'] = selected_component
        context['components'] = Component.objects.filter(salarygroupcomponent__salary_group=salary_group)
        try:
            salary_group_component = SalaryGroupComponent.objects.get(
                salary_group=salary_group,
                component=selected_component,
            )
        except SalaryGroupComponent.DoesNotExist as e:
            raise Http404('Salary group component does not exist') from e
        context['salary_group_component'] = salary_group_component

        if context['selected_item'] == 'mapped':
            context['selected_mapped_item'] = request.POST.get('mapping_policy')
        elif context['selected_item'] == 'rule-based':
            rbformset = self.rule_based_formset_class(
                request.POST,
                instance=salary_group_component.variable,
            )
            if rbformset.is_valid():
                rbformset.save()
                context['rbforms'] = rbformset
            else:
                messages.error(request, 'Invalid rule form')
                context['rbforms'] = rbformset
                return render(request, self.template_name, context)
        if 'rbforms' not in context:
            rbformset = self.rule_based_formset_class(
                instance=salary_group_component.variable,
            )
            context['rbforms'] = rbformset

        if not form.is_valid():
            return render(request, self.template_name, context)

        salary_group_component = \
            SalaryGroupComponent.objects.get(salary_group=salary_group, component=selected_component)

        salary_group_component.condition_type = selected_item
        if selected_item == 'mapped':
            salary_group_component.mapping_policy = request.POST.get('mapping_policy')
        salary_group_component.save()

        update_message = "Updated "+str(selected_component)+" for "+str(salary_group)+" group"
        messages.success(self.request, update_message)
        return render(request, self.template_name, context)

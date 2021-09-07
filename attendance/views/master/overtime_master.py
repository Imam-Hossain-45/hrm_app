__all__ = [
    'OvertimeMasterListView',
    'OvertimeMasterCreateView',
    'OvertimeMasterUpdateView',
    'OvertimeMasterDeleteView',
]

from cimbolic.models import Variable, Formula
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory, modelform_factory, RadioSelect
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DeleteView, ListView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse, reverse_lazy

from helpers.mixins import PermissionMixin
from attendance.models.master.overtime_master import *
from helpers.functions import get_organizational_structure


class OvertimeMasterListView(LoginRequiredMixin, PermissionMixin, ListView):
    """
    List all the overtime rules.
    URL: admin/attendance/master/overtime/
    """
    model = OvertimeRule
    template_name = 'attendance/master/overtime_master/list.html'
    permission_required = 'view_overtimerule'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        for ot in self.object_list:
            try:
                calc_model = ot.active_wage_calculation_model
            except ValueError as e:
                if str(e) == 'Exactly 1 wage calculation method must be active':
                    messages.error(
                        request,
                        'Exactly 1 wage calculation method must be active'
                        ' for Overtime: {}'.format(ot.name),
                    )
                    calc_model = 'N/A'
                else:
                    raise e
            ot.calc_model = calc_model
        context = self.get_context_data()
        return self.render_to_response(context)


class OvertimeMasterCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    """
    Create a new overtime rule.
    URL: admin/attendance/master/overtime/create/

    Note: Alternative implementation ideas for creating objects of other models
    that have a FK relationship to this view's model:
    - Manually create distinct forms in the template and parse the resulting
      POST data in this view manually.
    - Add links to views that create the objects at the end of this view's
      form. With AJAX, save this form so it has a pk (otherwise the related
      objects cannot be saved).
    """
    model = OvertimeRule
    fields = [
        'name', 'code', 'description', 'default_calculation_unit', 'segment',
        'buffer_duration_pre', 'buffer_duration_unit_pre', 'minimum_working_duration_pre',
        'minimum_working_duration_unit_pre', 'tolerance_time_pre', 'buffer_duration_post',
        'buffer_duration_unit_post', 'minimum_working_duration_post',
        'minimum_working_duration_unit_post', 'tolerance_time_post',
        'taxable',
    ]
    template_name = 'attendance/master/overtime_master/create.html'
    permission_required = 'add_overtimerule'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = modelform_factory(
                self.model,
                fields=self.fields,
                widgets={
                    'segment': RadioSelect,
                },
            )
        return super().get_form(form_class=form_class)

    def get_success_url(self):
        return reverse(
            'beehive_admin:attendance:overtime_update',
            kwargs={'pk': self.object.pk},
        )


class OvertimeMasterUpdateView(LoginRequiredMixin, PermissionMixin, SingleObjectMixin, TemplateView):
    """
    Update an overtime rule.
    URL: admin/attendance/master/overtime/<pk>/update/
    """
    model = OvertimeRule
    template_name = 'attendance/master/overtime_master/update.html'
    permission_required = 'change_overtimerule'

    overtimerule_form_class = modelform_factory(
        OvertimeRule,
        fields=[
            'name', 'code', 'description', 'default_calculation_unit', 'segment',
            'buffer_duration_pre', 'buffer_duration_unit_pre', 'minimum_working_duration_pre',
            'minimum_working_duration_unit_pre', 'tolerance_time_pre', 'buffer_duration_post',
            'buffer_duration_unit_post', 'minimum_working_duration_post',
            'minimum_working_duration_unit_post', 'tolerance_time_post',
            'taxable',
        ],
        widgets={
            'segment': RadioSelect,
        },
    )
    duration_restriction_formset_class = inlineformset_factory(
        OvertimeRule,
        OvertimeDurationRestriction,
        fields=['rule', 'ot_segment', 'scope_value', 'scope_unit', 'maximum_duration', 'maximum_duration_unit'],
        widgets={'ot_segment': RadioSelect},
        extra=0,
        min_num=1,
    )
    calc_fixedrate_form_class = modelform_factory(
        OvertimeWageCalculationFixedRate,
        fields=['rule', 'enabled', 'basis', 'scope_value', 'amount'],
    )
    calc_variable_form_class = modelform_factory(
        OvertimeWageCalculationVariable,
        fields=['rule', 'enabled', 'basis'],
    )
    calc_manual_form_class = modelform_factory(
        OvertimeWageCalculationManual,
        fields=['rule', 'enabled'],
    )
    calc_rulebased_form_class = modelform_factory(
        OvertimeWageCalculationRuleBased,
        fields=['rule', 'enabled', 'basis'],
    )
    calc_rulebased_formula_formset_class = inlineformset_factory(
        Variable,
        Formula,
        fields=['variable', 'priority', 'condition', 'rule'],
        extra=0,
        min_num=1,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        if 'form0' not in context:
            context['form0'] = self.overtimerule_form_class(
                instance=self.object,
            )
        if 'drforms' not in context:
            context['drforms'] = self.duration_restriction_formset_class(
                instance=self.object,
            )
        if 'form1' not in context:
            context['form1'] = self.calc_fixedrate_form_class(
                instance=self.object.fixed_rate_wage,
            )
        if 'form2' not in context:
            context['form2'] = self.calc_variable_form_class(
                instance=self.object.variable_wage,
            )
        if 'form3' not in context:
            context['form3'] = self.calc_manual_form_class(
                instance=self.object.manual_wage,
            )
        if 'form4' not in context:
            context['form4'] = self.calc_rulebased_form_class(
                instance=self.object.rule_based_wage,
            )
        if 'rbforms' not in context:
            context['rbforms'] = self.calc_rulebased_formula_formset_class(
                instance=self.object.rule_based_wage.variable,
            )
        return context

    def get_success_url(self):
        return reverse(
            'beehive_admin:attendance:overtime_update',
            kwargs={'pk': self.object.pk},
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'done' in request.POST:
            if self.object.count_enabled_wage_calculation_methods() != 1:
                messages.error(request, 'Exactly 1 amount calculation method may be active!')
                return self.get(request, *args, **kwargs)
            else:
                return HttpResponseRedirect(reverse('beehive_admin:attendance:overtime_list'))
        elif 'drforms' in request.POST:
            formset = self.duration_restriction_formset_class(
                request.POST, instance=self.object
            )
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Saved.')
                return HttpResponseRedirect(self.get_success_url())
            else:
                return self.render_to_response(self.get_context_data(drforms=formset))
        elif 'rbforms' in request.POST:
            formset = self.calc_rulebased_formula_formset_class(
                request.POST, instance=self.object.rule_based_wage.variable
            )
            if request.POST.get('rb_formset_enabled') == 'on':
                print(request.POST)
                formset = self.calc_rulebased_formula_formset_class(
                    request.POST, instance=self.object.rule_based_wage.variable
                )
                if formset.is_valid():
                    formset.save()
                    messages.success(request, 'Saved.')
                    return HttpResponseRedirect(self.get_success_url())
                else:
                    print('invalid', formset.errors)
            return self.render_to_response(self.get_context_data(drforms=formset))
        else:
            fid = request.POST.get('fid', 'form0')
            if fid == 'form1':
                form = self.calc_fixedrate_form_class(
                    request.POST, instance=self.object.fixed_rate_wage
                )
            elif fid == 'form2':
                form = self.calc_variable_form_class(
                    request.POST, instance=self.object.variable_wage
                )
            elif fid == 'form3':
                form = self.calc_manual_form_class(
                    request.POST, instance=self.object.manual_wage
                )
            elif fid == 'form4':
                form = self.calc_rulebased_form_class(
                    request.POST, instance=self.object.rule_based_wage
                )
                formset = self.calc_rulebased_formula_formset_class(
                    request.POST, instance=self.object.rule_based_wage.variable
                )
                if form.is_valid():
                    form.save()
                    if formset.is_valid():
                        formset.save()
                        messages.success(request, 'Saved.')
                        return HttpResponseRedirect(self.get_success_url())
                else:
                    if formset.is_valid():
                        formset.save()
                return self.render_to_response(self.get_context_data(fid=form, rbforms=formset))
            else:
                form = self.overtimerule_form_class(
                    request.POST, instance=self.object
                )
            if form.is_valid():
                obj = form.save()
                if fid == 'form0':
                    self.object = obj
                messages.success(request, 'Saved.')
                return HttpResponseRedirect(self.get_success_url())
            else:
                return self.render_to_response(self.get_context_data(**{fid: form}))


class OvertimeMasterDeleteView(LoginRequiredMixin, PermissionMixin, DeleteView):
    """
    Delete an overtime rule.
    URL: admin/attendance/master/overtime/<pk>/delete/
    """
    model = OvertimeRule
    success_url = reverse_lazy('beehive_admin:attendance:overtime_list')
    template_name = 'attendance/master/overtime_master/confirm_delete.html'
    permission_required = 'delete_overtimerule'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Deleted "{}".'.format(self.get_object()))
        return super().delete(request, *args, **kwargs)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect
from helpers.mixins import PermissionMixin
from payroll.models import DeductionComponent, EarlyOutSlab, EarlyOutSetting, EarlyOutSlabRBR
from payroll.forms import EarlyOutSlabForm
from django.contrib import messages
from django.forms import inlineformset_factory
from helpers.functions import get_organizational_structure


class EarlyOutSlabCreate(LoginRequiredMixin, PermissionMixin, FormView):
    """ Create EarlyOut policy slab """

    template_name = 'payroll/master/deduction/deduction_component/settings/early_out/create.html'
    permission_required = 'add_earlyoutslab'
    form_class = EarlyOutSlabForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['component'] = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))
        context['form'] = self.form_class()
        context['selected_condition_type'] = 'rule-based'
        context['selected_basis_type'] = 'day-basis'
        return context

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        form = EarlyOutSlabForm(request.POST)
        context['form'] = form
        context['component'] = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))

        time = request.POST.get('time')
        unit = request.POST.get('unit')
        days_to_consider = request.POST.get('days_to_consider')
        condition_type = request.POST.get('condition_type_options')
        basis_type = request.POST.get('basis_type_options')

        context['selected_condition_type'] = condition_type
        context['selected_basis_type'] = basis_type

        if (time and not time.isdigit()) or (days_to_consider and not days_to_consider.isdigit()):
            messages.error(self.request, "Invalid Input")
            return render(request, self.template_name, {**context})

        if not form.my_is_valid():
            messages.error(self.request, "Time field is required")
            return render(request, self.template_name, {**context})

        early_out_setting = EarlyOutSetting.objects.get(component=context['component'])
        calculated_time = int(time)
        if unit == 'hour':
            calculated_time = calculated_time * 60

        if early_out_setting.early_out_allowed_time:
            early_out_allowed_time = early_out_setting.early_out_allowed_time
            if early_out_setting.early_out_allowed_time_unit == 'hour':
                early_out_allowed_time = early_out_allowed_time * 60
            if calculated_time < early_out_allowed_time:
                messages.error(self.request, "Must be greater or equal than the allowed early out")
                return render(request, self.template_name, {**context})

        submitted_form = form.save(commit=False)
        submitted_form.component = context['component']
        submitted_form.time = time
        submitted_form.unit = unit
        submitted_form.days_to_consider = days_to_consider
        submitted_form.condition_type = condition_type
        submitted_form.basis_type = basis_type
        submitted_form.save()
        messages.success(self.request, "New slab for "+str(time)+" "+str(unit)+" is created")
        return redirect(
            reverse(
                'beehive_admin:payroll:early_out_slab_update',
                kwargs={'pk': context['component'].id, 'pk2': submitted_form.id},
            )
        )


class EarlyOutSlabUpdate(LoginRequiredMixin, PermissionMixin, FormView):
    """ Update EarlyOut policy slab """

    template_name = 'payroll/master/deduction/deduction_component/settings/early_out/update.html'
    permission_required = 'change_earlyoutslab'
    form_class = EarlyOutSlabForm
    rule_based_formset_class = inlineformset_factory(
        EarlyOutSlab,
        EarlyOutSlabRBR,
        fields=['priority', 'condition', 'rule', 'deduct_from', 'salary_component', 'leave_component'],
        extra=0,
        min_num=1,
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['component'] = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))
        slab = EarlyOutSlab.objects.get(id=self.kwargs.get('pk2', ''))
        initial = {
            'time': slab.time,
            'unit': slab.unit,
            'days_to_consider': slab.days_to_consider,
            'status': slab.status
        }
        context['rbinfo'] = {
            'fk_model': 'late_slab',
            'fk_id': slab.id,
        }
        context['rbforms'] = self.rule_based_formset_class(
            instance=slab,
        )
        context['form'] = self.form_class(initial=initial)
        context['selected_condition_type'] = slab.condition_type
        context['selected_basis_type'] = slab.basis_type
        return context

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        form = EarlyOutSlabForm(request.POST)
        context['form'] = form
        context['component'] = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))

        time = request.POST.get('time')
        unit = request.POST.get('unit')
        days_to_consider = request.POST.get('days_to_consider')
        condition_type = request.POST.get('condition_type_options')
        basis_type = request.POST.get('basis_type_options')
        status = request.POST.get('status')

        context['selected_condition_type'] = condition_type
        context['selected_basis_type'] = basis_type

        if (time and not time.isdigit()) or (days_to_consider and not days_to_consider.isdigit()):
            messages.error(self.request, "Invalid Input")
            return render(request, self.template_name, {**context})

        early_out_slab = EarlyOutSlab.objects.get(id=self.kwargs.get('pk2', ''))

        context['rbinfo'] = {
            'fk_model': 'late_slab',
            'fk_id': early_out_slab.id,
        }

        if condition_type == 'rule-based':
            rbformset = self.rule_based_formset_class(
                request.POST,
                instance=early_out_slab,
            )
            if rbformset.is_valid():
                rbformset.save()
                context['rbforms'] = rbformset
            else:
                messages.error(request, 'Invalid rule form')
                context['selected_condition_type'] = condition_type
                context['selected_basis_type'] = basis_type
                context['rbforms'] = rbformset
                return render(request, self.template_name, context)
        if 'rbforms' not in context:
            rbformset = self.rule_based_formset_class(
                instance=early_out_slab,
            )
            context['rbforms'] = rbformset

        if not form.my_is_valid():
            messages.error(self.request, "Time field is required")
            return render(request, self.template_name, {**context})

        early_out_setting = EarlyOutSetting.objects.get(component=context['component'])
        calculated_time = int(time)
        if unit == 'hour':
            calculated_time = calculated_time * 60

        if early_out_setting.early_out_allowed_time:
            early_out_allowed_time = early_out_setting.early_out_allowed_time
            if early_out_setting.early_out_allowed_time_unit == 'hour':
                early_out_allowed_time = early_out_allowed_time * 60
            if calculated_time < early_out_allowed_time:
                messages.error(self.request, "Must be greater or equal than the allowed early out")
                return render(request, self.template_name, {**context})

        early_out_slab.time = time
        early_out_slab.unit = unit
        early_out_slab.days_to_consider = days_to_consider
        early_out_slab.condition_type = condition_type
        early_out_slab.basis_type = basis_type
        early_out_slab.status = status
        early_out_slab.save()

        messages.success(self.request, "Slab for "+str(time)+" "+str(unit)+" is updated")
        return redirect(reverse_lazy('beehive_admin:payroll:deduction_early_out_settings',
                                     kwargs={'pk': context['component'].id}))


class EarlyOutSlabDelete(LoginRequiredMixin, PermissionMixin, TemplateView):
    """ Delete selected EarlyOut slab """

    permission_required = 'delete_earlyoutslab'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['component'] = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))
        context['early_out_slab'] = EarlyOutSlab.objects.get(id=self.kwargs.get('pk2', ''))
        return context

    def get(self, request, *args, **kwargs):
        # self.get_object() not working expected
        self.object = EarlyOutSlab.objects.get(id=self.kwargs.get('pk2', ''))
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        component = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))
        early_out_slab = EarlyOutSlab.objects.get(id=self.kwargs.get('pk2', ''))
        early_out_slab.delete()

        return redirect(reverse_lazy('beehive_admin:payroll:deduction_early_out_settings', kwargs={'pk': component.id}))

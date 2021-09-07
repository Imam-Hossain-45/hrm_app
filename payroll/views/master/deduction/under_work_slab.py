from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect
from helpers.mixins import PermissionMixin
from payroll.models import DeductionComponent, UnderWorkSlab, UnderWorkSlabRBR
from payroll.forms import UnderWorkSlabForm
from django.contrib import messages
from django.forms import inlineformset_factory
from helpers.functions import get_organizational_structure


class UnderWorkSlabCreate(LoginRequiredMixin, PermissionMixin, FormView):
    """ Create UnderWork policy slab """

    template_name = 'payroll/master/deduction/deduction_component/settings/under_work/create.html'
    permission_required = 'add_underworkslab'
    form_class = UnderWorkSlabForm

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
        form = UnderWorkSlabForm(request.POST)
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
                'beehive_admin:payroll:under_work_slab_update',
                kwargs={'pk': context['component'].id, 'pk2': submitted_form.id},
            )
        )


class UnderWorkSlabUpdate(LoginRequiredMixin, PermissionMixin, FormView):
    """ Update UnderWork policy slab """

    template_name = 'payroll/master/deduction/deduction_component/settings/under_work/update.html'
    permission_required = 'change_underworkslab'
    form_class = UnderWorkSlabForm
    rule_based_formset_class = inlineformset_factory(
        UnderWorkSlab,
        UnderWorkSlabRBR,
        fields=['priority', 'condition', 'rule', 'deduct_from', 'salary_component', 'leave_component'],
        extra=0,
        min_num=1,
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['component'] = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))
        slab = UnderWorkSlab.objects.get(id=self.kwargs.get('pk2', ''))
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
        form = UnderWorkSlabForm(request.POST)
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

        under_work_slab = UnderWorkSlab.objects.get(id=self.kwargs.get('pk2', ''))

        context['rbinfo'] = {
            'fk_model': 'late_slab',
            'fk_id': under_work_slab.id,
        }

        if condition_type == 'rule-based':
            rbformset = self.rule_based_formset_class(
                request.POST,
                instance=under_work_slab,
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
                instance=under_work_slab,
            )
            context['rbforms'] = rbformset

        if not form.my_is_valid():
            messages.error(self.request, "Time field is required")
            return render(request, self.template_name, {**context})

        under_work_slab.time = time
        under_work_slab.unit = unit
        under_work_slab.days_to_consider = days_to_consider
        under_work_slab.condition_type = condition_type
        under_work_slab.basis_type = basis_type
        under_work_slab.status = status
        under_work_slab.save()

        messages.success(self.request, "Slab for "+str(time)+" "+str(unit)+" is updated")
        return redirect(reverse_lazy('beehive_admin:payroll:deduction_under_work_settings',
                                     kwargs={'pk': context['component'].id}))


class UnderWorkSlabDelete(LoginRequiredMixin, PermissionMixin, TemplateView):
    """ Delete selected UnderWork slab """

    permission_required = 'delete_underworkslab'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['component'] = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))
        context['under_work_slab'] = UnderWorkSlab.objects.get(id=self.kwargs.get('pk2', ''))
        return context

    def get(self, request, *args, **kwargs):
        # self.get_object() not working expected
        self.object = UnderWorkSlab.objects.get(id=self.kwargs.get('pk2', ''))
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        component = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))
        under_work_slab = UnderWorkSlab.objects.get(id=self.kwargs.get('pk2', ''))
        under_work_slab.delete()

        return redirect(reverse_lazy('beehive_admin:payroll:deduction_under_work_settings', kwargs={'pk': component.id}))

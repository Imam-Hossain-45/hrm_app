from django.contrib.auth.mixins import LoginRequiredMixin
from helpers.mixins import PermissionMixin
from django.views.generic import View, FormView, ListView
from django.shortcuts import redirect, render
from payroll.models import (DeductionComponent, AbsentSetting, LateSetting, LateSlab, EarlyOutSetting, EarlyOutSlab,
                            UnderWorkSlab, AbsentSettingRBR)
from django.urls import reverse_lazy
from payroll.forms import AbsentSettingForm, LateSettingForm, EarlyOutSettingForm
from django.forms import inlineformset_factory
from django.contrib import messages
from helpers.functions import get_organizational_structure
from django.core.paginator import Paginator


class DeductionComponentSettingRedirect(View):
    def dispatch(self, request, *args, **kwargs):
        component = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))

        if component.deduction_component_type == 'absent':
            AbsentSetting.objects.get_or_create(component=component)
            return redirect(reverse_lazy('beehive_admin:payroll:deduction_absent_settings',
                                         kwargs={"pk": component.id}))
        elif component.deduction_component_type == 'late':
            LateSetting.objects.get_or_create(component=component)
            return redirect(reverse_lazy('beehive_admin:payroll:deduction_late_settings', kwargs={"pk": component.id}))
        elif component.deduction_component_type == 'early-out':
            EarlyOutSetting.objects.get_or_create(component=component)
            return redirect(reverse_lazy('beehive_admin:payroll:deduction_early_out_settings',
                                         kwargs={"pk": component.id}))
        elif component.deduction_component_type == 'under-work':
            return redirect(reverse_lazy('beehive_admin:payroll:deduction_under_work_settings',
                                         kwargs={"pk": component.id}))
        return redirect(reverse_lazy('beehive_admin:payroll:deduction_component_update', kwargs={"pk": component.id}))


class DeductionAbsentSetting(LoginRequiredMixin, PermissionMixin, FormView):
    """ Absent policy setup """

    template_name = 'payroll/master/deduction/deduction_component/settings/absent/update.html'
    permission_required = ['change_deductioncomponent', 'change_absentsetting']
    form_class = AbsentSettingForm

    rule_based_formset_class = inlineformset_factory(
        AbsentSetting,
        AbsentSettingRBR,
        fields=['priority', 'condition', 'rule', 'deduct_from', 'salary_component', 'leave_component'],
        extra=0,
        min_num=1,
    )

    def get_queryset(self):
        component = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))
        return AbsentSetting.objects.get(component=component)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        absent = self.get_queryset()
        initial = {
            'no_of_absent': absent.no_of_absent,
            'condition_type': absent.condition_type,
            'basis_type': absent.basis_type,
        }
        context['rbinfo'] = {
            'fk_model': 'absent_setting',
            'fk_id': absent.id,
        }
        context['rbforms'] = self.rule_based_formset_class(
            instance=absent,
        )
        context['form'] = self.form_class(initial=initial)
        context['selected_condition_type'] = absent.condition_type
        context['selected_basis_type'] = absent.basis_type
        return context

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        form = AbsentSettingForm(request.POST)
        context['form'] = form
        absent = self.get_queryset()

        no_of_absent = request.POST.get('no_of_absent')
        condition_type = request.POST.get('condition_type_options')
        basis_type = request.POST.get('basis_type_options')

        context['rbinfo'] = {
            'fk_model': 'absent_setting',
            'fk_id': absent.id,
        }

        if condition_type == 'rule-based':
            rbformset = self.rule_based_formset_class(
                request.POST,
                instance=absent,
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
                instance=absent,
            )
            context['rbforms'] = rbformset

        if not form.my_is_valid():
            context['selected_condition_type'] = condition_type
            context['selected_basis_type'] = basis_type
            messages.error(request, 'Invalid Form')
            return render(request, self.template_name, {**context})

        absent.no_of_absent = no_of_absent if no_of_absent else 0
        absent.condition_type = condition_type
        absent.basis_type = basis_type
        absent.save()

        context['selected_condition_type'] = absent.condition_type
        context['selected_basis_type'] = absent.basis_type

        update_message = "Updated "+str(absent.component)+" settings"
        messages.success(self.request, update_message)
        return render(request, self.template_name, {**context})


class DeductionLateSetting(LoginRequiredMixin, PermissionMixin, FormView):
    """ Late policy setup """

    template_name = 'payroll/master/deduction/deduction_component/settings/late/list.html'
    permission_required = ['change_deductioncomponent', 'change_latesetting']
    form_class = LateSettingForm

    def get_queryset(self):
        component = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))
        return LateSetting.objects.get(component=component)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        late = self.get_queryset()
        initial = {
            'late_grace_time': late.late_grace_time,
            'late_grace_time_unit': late.late_grace_time_unit,
            'late_last_time': late.late_last_time,
            'late_last_time_unit': late.late_last_time_unit
        }
        context['form'] = self.form_class(initial=initial)
        context['component'] = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))

        query_list = LateSlab.objects.filter(component=context['component']).order_by('id')
        paginator = Paginator(query_list, 50)
        page = self.request.GET.get('page')
        context['slabs'] = paginator.get_page(page)
        index = context['slabs'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        form = LateSettingForm(request.POST)
        context['form'] = form
        context['component'] = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))

        query_list = LateSlab.objects.filter(component=context['component']).order_by('id')
        paginator = Paginator(query_list, 50)
        page = self.request.GET.get('page')
        context['slabs'] = paginator.get_page(page)
        index = context['slabs'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        late_grace_time = request.POST.get('late_grace_time')
        late_last_time = request.POST.get('late_last_time')

        if (late_grace_time and not late_grace_time.isdigit()) or (late_last_time and not late_last_time.isdigit()):
            messages.error(self.request, "Invalid Input")
            return render(request, self.template_name, {**context})

        if not form.my_is_valid():
            messages.error(self.request, "Grace time must be lower than the last late time")
            return render(request, self.template_name, {**context})

        late_grace_time_unit = request.POST.get('late_grace_time_unit')
        late_last_time_unit = request.POST.get('late_last_time_unit')
        late = self.get_queryset()

        late.late_grace_time = int(late_grace_time) if late_grace_time else 0
        late.late_last_time = int(late_last_time) if late_last_time else 0

        late.late_grace_time_unit = late_grace_time_unit
        late.late_last_time_unit = late_last_time_unit
        late.save()

        messages.success(self.request, "Updated "+str(late.component)+" settings")
        return render(request, self.template_name, {**context})


class DeductionEarlyOutSetting(LoginRequiredMixin, PermissionMixin, FormView):
    """ Early out policy setup """

    template_name = 'payroll/master/deduction/deduction_component/settings/early_out/list.html'
    permission_required = ['change_deductioncomponent', 'change_earlyoutsetting']
    form_class = EarlyOutSettingForm

    def get_queryset(self):
        component = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))
        return EarlyOutSetting.objects.get(component=component)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        early_out = self.get_queryset()
        initial = {
            'early_out_allowed_time': early_out.early_out_allowed_time,
            'early_out_allowed_time_unit': early_out.early_out_allowed_time_unit
        }
        context['form'] = self.form_class(initial=initial)
        context['component'] = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))

        query_list = EarlyOutSlab.objects.filter(component=context['component']).order_by('id')
        paginator = Paginator(query_list, 50)
        page = self.request.GET.get('page')
        context['slabs'] = paginator.get_page(page)
        index = context['slabs'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        form = EarlyOutSettingForm(request.POST)
        context['form'] = form
        context['component'] = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))

        query_list = EarlyOutSlab.objects.filter(component=context['component']).order_by('id')
        paginator = Paginator(query_list, 50)
        page = self.request.GET.get('page')
        context['slabs'] = paginator.get_page(page)
        index = context['slabs'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        early_out_allowed_time = request.POST.get('early_out_allowed_time')

        if early_out_allowed_time and not early_out_allowed_time.isdigit():
            messages.error(self.request, "Invalid Input")
            return render(request, self.template_name, {**context})

        early_out_allowed_time_unit = request.POST.get('early_out_allowed_time_unit')
        early_out = self.get_queryset()

        early_out.early_out_allowed_time = int(early_out_allowed_time) if early_out_allowed_time else 0
        early_out.early_out_allowed_time_unit = early_out_allowed_time_unit
        early_out.save()

        messages.success(self.request, "Updated "+str(early_out.component)+" settings")
        return render(request, self.template_name, {**context})


class DeductionUnderWorkSetting(LoginRequiredMixin, PermissionMixin, ListView):
    """Show the list of all Under Work Slabs."""

    template_name = 'payroll/master/deduction/deduction_component/settings/under_work/list.html'
    model = UnderWorkSlab
    permission_required = ['view_underworkslab', 'add_underworkslab', 'change_underworkslab',
                           'delete_underworkslab']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['component'] = DeductionComponent.objects.get(id=self.kwargs.get('pk', ''))

        query_list = UnderWorkSlab.objects.filter(component=context['component']).order_by('id')
        paginator = Paginator(query_list, 50)
        page = self.request.GET.get('page')
        context['slabs'] = paginator.get_page(page)
        index = context['slabs'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context

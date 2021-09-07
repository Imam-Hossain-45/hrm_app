import functools
from typing import Callable, List
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import CreateView, ListView, DeleteView, UpdateView
from employees.forms import *
from employees.models import SalaryStructure, Payment
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse_lazy
from helpers.mixins import PermissionMixin
from django.contrib import messages
from django.utils.text import slugify
from payroll.models import EmployeeVariableSalary, SalaryGroup, SalaryGroupComponent
from django.db.models import Q
from helpers.functions import get_organizational_structure

# List of row ID's (DO NOT ACCESS UNLESS YOU KNOW WHAT YOU ARE DOING)
FORCEFULLY_CHANGED_COMPONENTS: List[int] = []


def clear_forcefully_changed_components(func: Callable) -> Callable:
    """Decorator to clear FORCEFULLY_CHANGED_COMPONENTS automatically."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        FORCEFULLY_CHANGED_COMPONENTS.clear()
        value = func(*args, **kwargs)
        forcefully_changed_components = SalaryGroupComponent.objects.filter(id__in=FORCEFULLY_CHANGED_COMPONENTS)
        for component in forcefully_changed_components:  # type: SalaryGroupComponent
            component.variable.formulae.all().delete()
        FORCEFULLY_CHANGED_COMPONENTS.clear()
        return value

    return wrapper


class EmployeeSalaryListView(LoginRequiredMixin, PermissionMixin, ListView):
    permission_required = 'view_salarystructure'
    template_name = 'employees/master/salary/list.html'
    model = SalaryStructure

    def get_context_data(self, *, object_list=None, **kwargs):
        get_list_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        salary_list = []
        pay = Payment.objects.filter(employee_id=self.kwargs['pk'])
        salary_structure = SalaryStructure.objects.filter(employee_id=self.kwargs['pk'])

        if pay.exists():
            pay_schedule = pay[0].get_pay_schedule_display()
        else:
            pay_schedule = ''

        for salary in salary_structure:
            if salary.salary_group.component:
                gross = EmployeeVariableSalary.objects.filter(salary_structure=salary,
                                                              component=salary.salary_group.component.get(
                                                                  is_gross=True))
                if gross.exists():
                    gross_amount = gross[0].value
                else:
                    gross_amount = 0.00
                if salary.to_date == date(9999, 12, 31):
                    to_date = ''
                else:
                    to_date = salary.to_date
                salary_dict = {
                    'from_date': salary.from_date,
                    'to_date': to_date,
                    'gross': gross_amount,
                    'pay_schedule': pay_schedule,
                    'change_reason': salary.reason_of_salary_modification,
                    'salary_group': salary.salary_group,
                    'salary_structure_id': salary.id,
                    'employee_id': self.kwargs['pk']
                }
                salary_list.append(salary_dict)

        paginator = Paginator(salary_list, 50)
        page = self.request.GET.get('page')
        salary_page_list = paginator.get_page(page)
        index = salary_page_list.number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        page_range = list(paginator.page_range)[start_index:end_index]

        context = {
            'salary_list': salary_page_list,
            'page_range': page_range,
            'pk': self.kwargs['pk'],
            'permissions': self.get_current_user_permission_list(),
            'org_items_list': get_organizational_structure(),
        }

        return context


def get_component(salary_group, salary_info):
    earning_component = []
    deduction_component = []
    if salary_group:
        if salary_info is not None:
            variable_salary_qs = EmployeeVariableSalary.objects.\
                filter(salary_structure=salary_info, salary_structure__salary_group=salary_group,
                       salary_structure__employee=salary_info.employee)
        else:
            variable_salary_qs = 0

        for com in salary_group.component.all():
            for condition in com.salarygroupcomponent_set.filter(salary_group=salary_group):
                value = ''
                if salary_info is not None and variable_salary_qs.count() > 0:
                    variable_salary = variable_salary_qs.filter(condition_type=condition.condition_type,
                                                                component=com)
                    if variable_salary.exists():
                        value = variable_salary[0].value

                if condition.component.component_type == 'earning':
                    earn_data = {'name': com.name, 'html_name': slugify(com.name), 'value': value,
                                 'condition_type': condition.condition_type}
                    earning_component.append(earn_data)
                if condition.component.component_type == 'deduction':
                    deduct_data = {'name': com.name, 'html_name': slugify(com.name), 'value': value,
                                   'condition_type': condition.condition_type}
                    deduction_component.append(deduct_data)

    return earning_component, deduction_component


class EmployeeSalaryCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Add new employee salary
        Access: Super-Admin, Admin
        Url: /employee/<pk>/salary/create
    """
    form_class = PaymentForm
    salary_form_class = SalaryStructureForm
    template_name = 'employees/master/salary/create.html'
    permission_required = ['add_salarystructure', 'change_salarystructure', 'view_salarystructure',
                           'delete_salarystructure']

    def get_queryset(self):
        return emp_models.SalaryStructure.objects.filter(employee_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']
        context['infinity_date'] = date(9999, 12, 31)
        if 'payment_form' not in context:
            payment_info = self.get_payment_information()
            if payment_info:
                context['payment_form'] = self.form_class(instance=payment_info)
            else:
                context['payment_form'] = self.form_class()
        if 'salary_form' not in context:
            salary_info = self.get_salary_information()
            if salary_info:
                component_data = get_component(salary_info.salary_group, salary_info)
                context['earning_component'], context['deduction_component'] = component_data
                context['salary_form'] = self.salary_form_class(instance=salary_info)
                context['salary_info'] = salary_info
            else:
                context['salary_form'] = self.salary_form_class()
        return context

    def get_payment_information(self):
        payment = emp_models.Payment.objects.filter(employee_id=self.kwargs['pk']).first()
        return payment

    def get_salary_information(self):
        salary = emp_models.SalaryStructure.objects.filter(employee_id=self.kwargs['pk']).last()
        return salary

    def render_to_response(self, context, **response_kwargs):
        """ Allow AJAX requests to be handled more gracefully """
        if self.request.is_ajax():
            group_id = self.request.GET.get('salary_group')
            if group_id is not '':
                salary_data = SalaryGroup.objects.get(id=group_id)
                earning_component, deduction_component = get_component(salary_data, salary_info=None)
                return render(self.request, 'employees/master/salary/salary_component_list.html',
                              {'earning_component': earning_component, 'deduction_component': deduction_component})
            else:
                return render(self.request, 'employees/master/salary/salary_component_list.html')
        else:
            return super(CreateView, self).render_to_response(context, **response_kwargs)

    @clear_forcefully_changed_components
    def post(self, request, *args, **kwargs):
        context = dict()
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        if 'payment_form' not in context:
            if self.get_payment_information():
                context['payment_form'] = self.form_class(instance=self.get_payment_information())
            else:
                context['payment_form'] = self.form_class()
        if 'salary_form' not in context:
            salary_info = self.get_salary_information()
            if salary_info:
                context['earning_component'], context['deduction_component'] = get_component(
                    salary_info.salary_group, salary_info)
                context['salary_form'] = self.salary_form_class(instance=salary_info)
            else:
                context['salary_form'] = self.salary_form_class()
        context['pk'] = self.kwargs['pk']
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        if 'form1' in request.POST:
            context['payment_form'] = self.form_class(request.POST)
            payment_form = context['payment_form']
            if payment_form.is_valid():
                obj, created = emp_models.Payment.objects.update_or_create(employee_id=self.kwargs['pk'], defaults={
                    'payment_mode': payment_form.cleaned_data['payment_mode'],
                    'pay_schedule': payment_form.cleaned_data['pay_schedule'],
                    'employee_bank_name': payment_form.cleaned_data['employee_bank_name'],
                    'employee_bank_AC_name': payment_form.cleaned_data['employee_bank_AC_name'],
                    'bank_branch_code': payment_form.cleaned_data['bank_branch_code'],
                    'bank_AC_no': payment_form.cleaned_data['bank_AC_no'],
                    'routing_number': payment_form.cleaned_data['routing_number']})
                if created:
                    messages.success(self.request, "Created payment information.")
                else:
                    messages.success(self.request, "Updated payment information.")
                return redirect('employees:employee_salary_create', self.kwargs['pk'])
        elif 'form2' in request.POST:
            context['salary_form'] = self.salary_form_class(request.POST)
            salary_form = context['salary_form']
            if salary_form.is_valid():
                if salary_form.cleaned_data['to_date'] in ['', None]:
                    to_date = date(9999, 12, 31)
                else:
                    to_date = salary_form.cleaned_data['to_date']
                structure_qs = emp_models.SalaryStructure.objects
                overlap_qs = structure_qs.filter(employee_id=self.kwargs['pk']).filter(
                    Q(from_date__gte=salary_form.cleaned_data['from_date'],
                      from_date__lte=to_date) | Q(
                        to_date__gte=salary_form.cleaned_data['from_date'],
                        to_date__lte=to_date) | Q(
                        from_date__lte=salary_form.cleaned_data['from_date'],
                        to_date__gte=to_date))
                if overlap_qs.count() > 0:
                    messages.error(request, "Cannot create salary structure in this date range.")
                else:
                    created = structure_qs.create(employee_id=self.kwargs['pk'],
                                                  from_date=salary_form.cleaned_data[
                                                      'from_date'],
                                                  salary_group=salary_form.cleaned_data[
                                                      'salary_group'],
                                                  bonus_group=salary_form.cleaned_data['bonus_group'],
                                                  to_date=to_date,
                                                  reason_of_salary_modification=
                                                  salary_form.cleaned_data[
                                                      'reason_of_salary_modification'])
                    if created:
                        salary_group = created.salary_group
                        variable_qs = EmployeeVariableSalary.objects
                        for com in salary_group.component.all():
                            for condition in com.salarygroupcomponent_set.filter(
                                    salary_group=salary_group):
                                if request.POST.get(slugify(com.name)) not in ['', None]:
                                    if condition.condition_type == 'variable':
                                        value = request.POST.get(slugify(com.name))
                                        condition.variable.formulae.all().delete()
                                        condition.variable.add_formula('NULL', '{}'.format(value), 1)
                                        FORCEFULLY_CHANGED_COMPONENTS.append(condition.id)

                                        variable_qs.update_or_create(salary_structure=created, component=com, defaults={
                                            'condition_type': condition.condition_type, 'value': value})
                        for com in salary_group.component.all():
                            for condition in com.salarygroupcomponent_set.filter(
                                    salary_group=salary_group):
                                if condition.condition_type == 'variable':
                                    continue
                                else:
                                    if request.POST.get(slugify(com.name)) in ['', None]:
                                        if condition.condition_type == 'rule-based':
                                            value = 0
                                            try:
                                                value = condition.variable.to_value()
                                            except Exception:
                                                pass
                                        else:
                                            value = 0
                                    else:
                                        value = 0
                                variable_qs.update_or_create(salary_structure=created, component=com, defaults={
                                    'condition_type': condition.condition_type, 'value': value})
                        messages.success(self.request, "Created salary information.")
                        return redirect('employees:employee_salary_create', self.kwargs['pk'])
        else:
            context['salary_form'] = self.salary_form_class(request.POST)
            salary_form = context['salary_form']
            if salary_form.is_valid():
                if salary_form.cleaned_data['to_date'] in ['', None]:
                    to_date = date(9999, 12, 31)
                else:
                    to_date = salary_form.cleaned_data['to_date']
                structured_id = request.POST.get('salary_structure_id')
                if structured_id not in ['', None, 'None']:
                    structure_qs = emp_models.SalaryStructure.objects
                    overlap_qs = structure_qs.exclude(id=structured_id).filter(employee_id=self.kwargs['pk']).filter(
                        Q(from_date__gte=salary_form.cleaned_data['from_date'],
                          from_date__lte=to_date) | Q(
                            to_date__gte=salary_form.cleaned_data['from_date'],
                            to_date__lte=to_date) | Q(
                            from_date__lte=salary_form.cleaned_data['from_date'],
                            to_date__gte=to_date))
                    if overlap_qs.count() > 0:
                        messages.error(request, "Cannot create salary structure in this date range.")
                    else:
                        updated = structure_qs.filter(id=structured_id).update(employee_id=self.kwargs['pk'],
                                                                               from_date=salary_form.cleaned_data[
                                                                                   'from_date'],
                                                                               salary_group=salary_form.cleaned_data[
                                                                                   'salary_group'],
                                                                               bonus_group=salary_form.cleaned_data[
                                                                                   'bonus_group'],
                                                                               to_date=to_date,
                                                                               reason_of_salary_modification=
                                                                               salary_form.cleaned_data[
                                                                                   'reason_of_salary_modification'])
                        if updated:
                            salary_group = salary_form.cleaned_data['salary_group']
                            variable_qs = EmployeeVariableSalary.objects
                            variable = []
                            for com in salary_group.component.all():
                                for condition in com.salarygroupcomponent_set.filter(
                                        salary_group=salary_group):
                                    if request.POST.get(slugify(com.name)) not in ['', None]:
                                        if condition.condition_type == 'variable':
                                            value = request.POST.get(slugify(com.name))
                                            condition.variable.formulae.all().delete()
                                            condition.variable.add_formula('NULL', '{}'.format(value), 1)
                                            FORCEFULLY_CHANGED_COMPONENTS.append(condition.id)

                                            updated, created = variable_qs.update_or_create(
                                                salary_structure_id=structured_id, component=com,
                                                defaults={'condition_type': condition.condition_type, 'value': value}
                                            )
                                            variable.append(updated.pk)

                            for com in salary_group.component.all():
                                for condition in com.salarygroupcomponent_set.filter(
                                        salary_group=salary_group):
                                    if request.POST.get(slugify(com.name)) not in ['', None]:
                                        if condition.condition_type == 'variable':
                                            continue
                                        elif condition.condition_type == 'rule-based':
                                            value = 0
                                            try:
                                                value = condition.variable.to_value()
                                            except Exception:
                                                pass
                                        else:
                                            value = 0
                                    else:
                                        value = 0
                                    updated, created = variable_qs.update_or_create(
                                        salary_structure_id=structured_id, component=com,
                                        defaults={'condition_type': condition.condition_type, 'value': value}
                                    )
                                    variable.append(updated.pk)
                            variable_qs.filter(salary_structure_id=structured_id).exclude(id__in=variable).delete()
                            messages.success(self.request, "Updated salary information.")
                            return redirect('employees:employee_salary_create', self.kwargs['pk'])

        return render(request, self.template_name, context)


class EmployeeSalaryUpdateView(LoginRequiredMixin, PermissionMixin, UpdateView):
    permission_required = 'change_salarystructure'
    template_name = 'employees/master/salary/update.html'
    form_class = SalaryStructureForm

    def get_queryset(self):
        salary = emp_models.SalaryStructure.objects.filter(id=self.kwargs['pk'])
        return salary

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['employee_id'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['employee_id']
        context['employee_id'] = self.kwargs['employee_id']
        context['infinity_date'] = date(9999, 12, 31)
        if 'salary_form' not in context:
            salary_info = self.get_queryset().first()
            if salary_info:
                component_data = get_component(salary_info.salary_group, salary_info)
                context['earning_component'], context['deduction_component'] = component_data
                context['salary_form'] = self.form_class(instance=salary_info)
        return context

    def render_to_response(self, context, **response_kwargs):
        """ Allow AJAX requests to be handled more gracefully """
        if self.request.is_ajax():
            group_id = self.request.GET.get('salary_group')
            if group_id is not '':
                salary_data = SalaryGroup.objects.get(id=group_id)
                earning_component, deduction_component = get_component(salary_data, salary_info=None)
                return render(self.request, 'employees/master/salary/salary_component_list.html',
                              {'earning_component': earning_component, 'deduction_component': deduction_component})
            else:
                return render(self.request, 'employees/master/salary/salary_component_list.html')
        else:
            return super(UpdateView, self).render_to_response(context, **response_kwargs)

    def post(self, request, *args, **kwargs):
        context = dict()
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['employee_id'])
        if 'salary_form' not in context:
            salary_info = self.get_queryset().first()
            if salary_info:
                context['earning_component'], context['deduction_component'] = get_component(
                    salary_info.salary_group, salary_info)
                context['salary_form'] = self.form_class(instance=salary_info)
        if request.POST:
            context['salary_form'] = self.form_class(request.POST)
            salary_form = context['salary_form']
            if salary_form.is_valid():
                if salary_form.cleaned_data['to_date'] in ['', None]:
                    to_date = date(9999, 12, 31)
                else:
                    to_date = salary_form.cleaned_data['to_date']
                structure_qs = emp_models.SalaryStructure.objects
                overlap_qs = structure_qs.exclude(id=self.kwargs['pk']).filter(employee_id=self.kwargs['pk']).filter(
                    Q(from_date__gte=salary_form.cleaned_data['from_date'],
                      from_date__lte=to_date) | Q(
                        to_date__gte=salary_form.cleaned_data['from_date'],
                        to_date__lte=to_date) | Q(
                        from_date__lte=salary_form.cleaned_data['from_date'],
                        to_date__gte=to_date))
                if overlap_qs.count() > 0:
                    messages.error(request, "Cannot update salary structure in this date range.")
                else:
                    updated = structure_qs.filter(id=self.kwargs['pk']).update(employee_id=self.kwargs['employee_id'],
                                                                               from_date=salary_form.cleaned_data[
                                                                                   'from_date'],
                                                                               salary_group=salary_form.cleaned_data[
                                                                                   'salary_group'],
                                                                               bonus_group=salary_form.cleaned_data[
                                                                                   'bonus_group'],
                                                                               to_date=to_date,
                                                                               reason_of_salary_modification=
                                                                               salary_form.cleaned_data[
                                                                                   'reason_of_salary_modification'])
                    if updated:
                        salary_group = salary_form.cleaned_data['salary_group']
                        variable_qs = EmployeeVariableSalary.objects
                        variable = []
                        for com in salary_group.component.all():
                            for condition in com.salarygroupcomponent_set.filter(
                                    salary_group=salary_group):
                                if request.POST.get(slugify(com.name)) not in ['', None]:
                                    if condition.condition_type == 'variable':
                                        value = request.POST.get(slugify(com.name))
                                        condition.variable.formulae.all().delete()
                                        condition.variable.add_formula('NULL', '{}'.format(value), 1)
                                        FORCEFULLY_CHANGED_COMPONENTS.append(condition.id)

                                        updated, created = variable_qs.update_or_create(
                                            salary_structure_id=self.kwargs['pk'], component=com,
                                            defaults={'condition_type': condition.condition_type, 'value': value}
                                        )
                                        variable.append(updated.pk)

                        for com in salary_group.component.all():
                            for condition in com.salarygroupcomponent_set.filter(salary_group=salary_group):
                                if request.POST.get(slugify(com.name)) not in ['', None]:
                                    if condition.condition_type == 'variable':
                                        continue
                                    elif condition.condition_type == 'rule-based':
                                        value = 0
                                        try:
                                            value = condition.variable.to_value()
                                        except Exception:
                                            pass
                                    else:
                                        value = 0
                                else:
                                    value = 0
                                updated, created = variable_qs.update_or_create(salary_structure_id=self.kwargs['pk'],
                                                                                component=com, defaults={
                                        'condition_type': condition.condition_type, 'value': value})
                                variable.append(updated.id)
                        variable_qs.filter(salary_structure_id=self.kwargs['pk']).exclude(id__in=variable).delete()
                        messages.success(self.request, "Updated salary information.")
                        return redirect('employees:employee_salary_list', self.kwargs['employee_id'])

        context['employee_id'] = self.kwargs['employee_id']
        context['pk'] = self.kwargs['pk']
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return render(request, self.template_name, context)


class EmployeeSalaryDeleteView(LoginRequiredMixin, PermissionMixin, DeleteView):
    permission_required = 'delete_salarystructure'
    model = emp_models.SalaryStructure
    success_message = "Deleted successfully."

    def get_context_data(self, **kwargs):
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['employee_id'])
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.error(self.request, self.success_message % obj.__dict__)
        return super(EmployeeSalaryDeleteView, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('employees:employee_salary_list', kwargs={'pk': self.object.employee.id})

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import ListView, DetailView, UpdateView
from leave.forms import SearchForm
from helpers.functions import execute_leave_deductions, get_employee_query_info
from helpers.mixins import PermissionMixin
from payroll.models import EmployeeSalary, PaymentDisbursedInfo, SalaryPaymentMethod
from django.contrib import messages
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from payroll.forms import PaymentForm, DisburseForm, DisburseGroupForm
from django.core.validators import EMPTY_VALUES
from decimal import Decimal
from datetime import datetime
from helpers.functions import get_organizational_structure
from employees.models import EmployeeIdentification


def EmployeeFilter(employee, from_date, to_date, company, division, department, business_unit, branch, schedule,
                   status):
    if employee not in EMPTY_VALUES or from_date not in EMPTY_VALUES \
        or to_date not in EMPTY_VALUES or company not in ['',None] or division not in ['', None] or \
        department not in EMPTY_VALUES or business_unit not in EMPTY_VALUES or branch not in ['', None] or \
            schedule not in ['', None]:

        object_list = EmployeeSalary.objects.filter(status__in=status)
        if employee not in EMPTY_VALUES:
            object_list = object_list.filter(employee=employee)
        if from_date not in EMPTY_VALUES and to_date not in EMPTY_VALUES:
            object_list = object_list.filter(start_date__gte=from_date, end_date__lte=to_date)
        if company not in EMPTY_VALUES:
            object_list = object_list.filter(employee__employee_job_informations__company=company)
        if division not in EMPTY_VALUES:
            object_list = object_list.filter(employee__employee_job_informations__division=division)
        if department not in EMPTY_VALUES:
            object_list = object_list.filter(employee__employee_job_informations__department=department)
        if business_unit not in EMPTY_VALUES:
            object_list = object_list.filter(employee__employee_job_informations__business_unit=business_unit)
        if branch not in EMPTY_VALUES:
            object_list = object_list.filter(employee__employee_job_informations__branch=branch)
        if schedule not in EMPTY_VALUES:
            object_list = object_list.filter(employee__employee_attendance__schedule_type=schedule)

        return object_list.order_by('created_at')


class SalaryDisbursementGenerate(LoginRequiredMixin, PermissionMixin, ListView):
    template_name = 'payroll/process/salary_disbursement/list.html'
    model = EmployeeSalary
    permission_required = 'view_employeesalary'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = ''
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['search_form'] = SearchForm(self.request.GET)
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')
        company = self.request.GET.get('company')
        division = self.request.GET.get('division')
        department = self.request.GET.get('department')
        business_unit = self.request.GET.get('business_unit')
        branch = self.request.GET.get('branch')
        schedule = self.request.GET.get('schedule')

        if self.request.GET.get('query'):
            employee = self.request.GET.get('employee')

        if employee:
            context['employee'] = get_employee_query_info(employee)

        disbursement_list = EmployeeFilter(employee, from_date, to_date, company, division, department,
                                           business_unit, branch, schedule, ['confirmed', 'disbursed'])

        if disbursement_list:
            paginator = Paginator(disbursement_list, 50)
            page = self.request.GET.get('page')
            context['disbursement_list'] = paginator.get_page(page)
            index = context['disbursement_list'].number - 1
            max_index = len(paginator.page_range)
            start_index = index - 0 if index >= 3 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            context['page_range'] = list(paginator.page_range)[start_index:end_index]
            context['path'] = "%s" % "&".join(["%s=%s" % (key, value) for (key, value) in self.request.GET.items()
                                               if not key == 'page'])

        context['objects'] = disbursement_list
        return context

    def post(self, *args, **kwargs):
        employee_salary_id = self.request.POST.getlist('employee_salary_id')
        if employee_salary_id not in EMPTY_VALUES:
            return HttpResponseRedirect(
                reverse('beehive_admin:payroll:salary_disbursement_all', args=[employee_salary_id]))
        else:
            messages.error(self.request, "No employee checked.")
        return redirect('beehive_admin:payroll:salary_disbursement')


def get_details(id, status):
    try:
        object_list = EmployeeSalary.objects.get(id=id, status=status)
        change_method_data = object_list.salary_payment_method
        data = {}
        if change_method_data.exists():
            for payment in change_method_data.all():
                data = {
                    'salary_payment_method_id': payment.id,
                    'mode': payment.get_payment_mode_display(),
                    'mode_value': payment.payment_mode,
                }
                payment_list = []
                disburse_payment = payment.disburse_payment_method.filter(payment_method=payment)
                for disburse in disburse_payment:
                    disburse_dict = {'bank_name': disburse.employee_bank_name,
                                     'account_name': disburse.employee_bank_AC_name,
                                     'branch_code': disburse.bank_branch_code, 'ac_no': disburse.bank_AC_no,
                                     'routing_number': disburse.routing_number,
                                     'mixed_mode': disburse.get_payment_mode_for_mixed_display(),
                                     'mixed_mode_value': disburse.payment_mode_for_mixed,
                                     'fintech_service': disburse.fintech_service,
                                     'cheque_number': disburse.cheque_number, 'mobile_number': disburse.mobile_number,
                                     'disburse_amount': disburse.disbursed_amount
                                     }
                    payment_list.append(disburse_dict)
                data['disburse_list'] = payment_list
        return object_list, data
    except:
        return False


class SalaryDisbursementDetails(LoginRequiredMixin, PermissionMixin, DetailView):
    template_name = 'payroll/process/salary_disbursement/details.html'
    model = EmployeeSalary
    permission_required = 'view_employeesalary'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        object_list, data = get_details(self.kwargs['pk'], 'confirmed')
        context['object_list'] = object_list
        context['payment_details'] = data
        return context

    def post(self, request, *args, **kwargs):
        if 'disburse' in request.POST:
            employee_salary_qs = EmployeeSalary.objects.filter(id=self.kwargs['pk'])
            employee_salary_qs.update(disbursed_date=datetime.now(), status='disbursed')
            employee_salary = employee_salary_qs.get()
            execute_leave_deductions(employee_salary)
            messages.success(self.request, "Disbursed.")
            return redirect('beehive_admin:payroll:salary_disbursement')

        return render(request, self.get_context_data())


class SalaryDisbursementEdit(LoginRequiredMixin, PermissionMixin, UpdateView):
    template_name = 'payroll/process/salary_disbursement/edit.html'
    form_class = PaymentForm
    second_form_class = DisburseForm
    permission_required = 'view_employeesalary'

    def get_queryset(self):
        return SalaryPaymentMethod.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        object_list, data = get_details(self.kwargs['pk'], 'confirmed')
        context['object_list'] = object_list
        context['payment_details'] = data
        context['form'] = self.form_class(instance=self.object)
        context['disbursed_list'] = self.get_disburse_info(self.object)
        context['disburse_form'] = self.second_form_class()
        return context

    def get_disburse_info(self, salary_mode):
        disburse_qs = PaymentDisbursedInfo.objects.filter(payment_method=salary_mode)
        disburse_list = []
        for disburse in disburse_qs:
            if disburse.employee_bank_name:
                bank_name = disburse.employee_bank_name.id
            else:
                bank_name = ''
            bank_AC_no = None if disburse.bank_AC_no is 0 else disburse.bank_AC_no
            cheque_number = None if disburse.cheque_number is 0 else disburse.cheque_number
            disburse_dict = {
                'payment_mode_for_mixed': disburse.payment_mode_for_mixed,
                'employee_bank_name': bank_name,
                'employee_bank_AC_name': disburse.employee_bank_AC_name,
                'bank_branch_code': disburse.bank_branch_code,
                'bank_AC_no': bank_AC_no,
                'routing_number': disburse.routing_number,
                'cheque_number': cheque_number,
                'fintech_service': disburse.fintech_service,
                'mobile_number': disburse.mobile_number,
                'disbursed_amount': disburse.disbursed_amount,
            }
            disburse_list.append(disburse_dict)
        return disburse_list

    def post(self, request, *args, **kwargs):
        salary_mode = self.get_queryset().filter(employee_salary_id=self.kwargs['pk']).last()
        context = dict()
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        object_list, data = get_details(self.kwargs['pk'], 'confirmed')
        context['object_list'] = object_list
        context['payment_details'] = data
        form = self.form_class(request.POST, instance=salary_mode)
        context['form'] = form
        disburse_form = self.second_form_class(request.POST)
        context['disburse_form'] = disburse_form

        if form.is_valid() and disburse_form.is_valid():
            updated, created = SalaryPaymentMethod.objects.update_or_create(employee_salary_id=self.kwargs['pk'],
                                                                            defaults={
                                                                                'payment_mode': form.cleaned_data[
                                                                                    'payment_mode']})
            if updated:
                payment_method_id = updated.id
            else:
                payment_method_id = created.pk

            disburse_qs = PaymentDisbursedInfo.objects
            disburse_qs.filter(payment_method_id=payment_method_id).delete()

            if form.cleaned_data.get('payment_mode') == 'bank':
                disburse_qs.create(payment_method_id=payment_method_id,
                                   employee_bank_name=disburse_form.cleaned_data.get(
                                       'employee_bank_name'),
                                   employee_bank_AC_name=disburse_form.cleaned_data.get(
                                       'employee_bank_AC_name'),
                                   bank_branch_code=disburse_form.cleaned_data.get(
                                       'bank_branch_code'),
                                   bank_AC_no=disburse_form.cleaned_data.get(
                                       'bank_AC_no'),
                                   routing_number=disburse_form.cleaned_data.get(
                                       'routing_number'),
                                   cheque_number=None,
                                   fintech_service='',
                                   mobile_number='',
                                   disbursed_amount=0.00)
            elif form.cleaned_data.get('payment_mode') == 'cash':
                disburse_qs.create(payment_method_id=payment_method_id, employee_bank_name_id='',
                                   employee_bank_AC_name='',
                                   bank_branch_code='',
                                   bank_AC_no=None,
                                   routing_number='',
                                   cheque_number=None,
                                   fintech_service='',
                                   mobile_number='',
                                   disbursed_amount=0.00)
            elif form.cleaned_data.get('payment_mode') == 'cheque':
                disburse_qs.create(payment_method_id=payment_method_id, payment_mode_for_mixed='',
                                   employee_bank_name_id='',
                                   employee_bank_AC_name='',
                                   bank_branch_code='',
                                   bank_AC_no=None,
                                   routing_number='',
                                   cheque_number=disburse_form.cleaned_data.get(
                                       'cheque_number'),
                                   fintech_service='',
                                   mobile_number='',
                                   disbursed_amount=0.00)
            elif form.cleaned_data.get('payment_mode') == 'fintech':
                disburse_qs.create(payment_method_id=payment_method_id, payment_mode_for_mixed='',
                                   employee_bank_name_id='',
                                   employee_bank_AC_name='',
                                   bank_branch_code='',
                                   bank_AC_no=None,
                                   routing_number='',
                                   cheque_number=None,
                                   fintech_service=disburse_form.cleaned_data.get(
                                       'fintech_service'),
                                   mobile_number=disburse_form.cleaned_data.get(
                                       'mobile_number'),
                                   disbursed_amount=0.00)
            else:
                payment_mode_for_mixed = request.POST.getlist('payment_mode_for_mixed')
                mixed_bank_name = request.POST.getlist('mixed_bank_name')
                mixed_bank_account_name = request.POST.getlist('mixed_bank_account_name')
                mixed_branch_code = request.POST.getlist('mixed_branch_code')
                mixed_ac_no = request.POST.getlist('mixed_ac_no')
                mixed_routing_no = request.POST.getlist('mixed_routing_no')
                mixed_cheque_number = request.POST.getlist('mixed_cheque_number')
                mixed_service = request.POST.getlist('mixed_service')
                mixed_mobile_number = request.POST.getlist('mixed_mobile_number')
                disbursed_amount = request.POST.getlist('disbursed_amount')
                for i, payment_mode in enumerate(payment_mode_for_mixed):
                    if payment_mode not in EMPTY_VALUES:
                        try:
                            mixed_ac = int(mixed_ac_no[i])
                        except:
                            mixed_ac = None

                        try:
                            mixed_cheque = int(mixed_cheque_number[i])
                        except:
                            mixed_cheque = None
                        disburse_qs.create(payment_method_id=payment_method_id,
                                           payment_mode_for_mixed=payment_mode_for_mixed[i],
                                           employee_bank_name_id=mixed_bank_name[i],
                                           employee_bank_AC_name=mixed_bank_account_name[i],
                                           bank_branch_code=mixed_branch_code[i],
                                           bank_AC_no=mixed_ac,
                                           routing_number=mixed_routing_no[i],
                                           cheque_number=mixed_cheque,
                                           fintech_service=mixed_service[i],
                                           mobile_number=mixed_mobile_number[i],
                                           disbursed_amount=Decimal(disbursed_amount[i]))
            if 'disburse' in request.POST:
                employee_salary_qs = EmployeeSalary.objects.filter(id=self.kwargs['pk'])
                employee_salary_qs.update(
                    disbursed_date=disburse_form.cleaned_data.get('disbursed_date'),
                    status='disbursed')
                employee_salary = employee_salary_qs.get()
                execute_leave_deductions(employee_salary)
                messages.success(self.request, "Disbursed.")
            else:
                EmployeeSalary.objects.filter(id=self.kwargs['pk']).update(status='draft')
                messages.success(self.request, "Saved.")
            return redirect('beehive_admin:payroll:salary_disbursement')
        return render(request, self.template_name, context)


class SalaryDisbursementGroup(LoginRequiredMixin, PermissionMixin, ListView):
    template_name = 'payroll/process/salary_disbursement/group_list.html'
    model = EmployeeSalary
    permission_required = 'view_employeesalary'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        import re
        em_salary_id = re.findall('\d+', self.kwargs['pk'])
        employee_list = []
        for salary_id in em_salary_id:
            try:
                object_list = EmployeeSalary.objects.get(id=salary_id, status='confirmed')
                employee_list.append(object_list)
            except:
                pass
        context['employee_list'] = employee_list
        context['group_form'] = DisburseGroupForm()
        return context

    def post(self, request, *args, **kwargs):
        context = dict()
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        import re
        em_salary_id = re.findall('\d+', self.kwargs['pk'])
        employee_list = []
        for salary_id in em_salary_id:
            object_list = EmployeeSalary.objects.get(id=salary_id, status='confirmed')
            employee_list.append(object_list)
        context['employee_list'] = employee_list
        group_form = DisburseGroupForm(request.POST)
        context['group_form'] = group_form
        if group_form.is_valid():
            em_salary = request.POST.getlist('employee_salary_id')
            em_payment_method = request.POST.getlist('employee_payment_method')
            disbursed_date = request.POST.getlist('disbursed_date')
            for i, id in enumerate(em_salary):
                employee_salary_qs = EmployeeSalary.objects.filter(id=id)
                employee_salary_qs.update(status='disbursed', disbursed_date=disbursed_date[i])
                employee_salary = employee_salary_qs.get()
                execute_leave_deductions(employee_salary)
                if em_payment_method[i] == 'cheque':
                    name = str('cheque_number__') + str(id)
                    PaymentDisbursedInfo.objects.filter(payment_method__employee_salary_id=em_salary[i]).update(
                        cheque_number=request.POST[name])

            messages.success(self.request, "Disbursed.")
            return redirect('beehive_admin:payroll:salary_disbursement')
        return render(request, self.template_name, context)


class SalaryBreakdownlList(LoginRequiredMixin, PermissionMixin, ListView):
    template_name = 'payroll/process/salary_disbursement/salary_list.html'
    model = EmployeeSalary
    permission_required = 'view_employeesalary'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        earning_component = []
        deduction_component = []
        object_list = EmployeeSalary.objects.get(id=self.kwargs['pk'])
        context['object_list'] = object_list
        for obj in object_list.payslipcomponent_set.all():
            if obj.component.component_type == 'earning':
                earn_data = {'name': obj.component, 'value': obj.value}
                earning_component.append(earn_data)
            if obj.component.component_type == 'deduction':
                deduct_data = {'name': obj.component, 'value': obj.value}
                deduction_component.append(deduct_data)
        context['earning_component'] = earning_component
        context['deduction_component'] = deduction_component
        return context

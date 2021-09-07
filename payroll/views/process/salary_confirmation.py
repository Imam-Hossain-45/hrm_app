from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import ListView
from leave.forms import SearchForm
from helpers.mixins import PermissionMixin
from payroll.models import EmployeeSalary
from django.contrib import messages
from django.shortcuts import render, redirect
from helpers.functions import get_organizational_structure, get_employee_query_info


def EmployeeFilter(employee, from_date, to_date, company, division, department, business_unit, branch, schedule, status):
    if employee not in ['', None] or from_date not in ['', None] or to_date not in ['', None] or \
        company not in ['', None] or division not in ['', None] or department not in ['', None] or \
            business_unit not in ['', None] or branch not in ['', None] or schedule not in ['', None]:

        object_list = EmployeeSalary.objects.filter(status__in=status)
        if employee not in ['', None]:
            object_list = object_list.filter(employee=employee)
        if from_date not in ['', None] and to_date not in ['', None]:
            object_list = object_list.filter(start_date__gte=from_date, end_date__lte=to_date)
        if company not in ['', None]:
            object_list = object_list.filter(employee__employee_job_informations__company=company)
        if division not in ['', None]:
            object_list = object_list.filter(employee__employee_job_informations__division=division)
        if department not in ['', None]:
            object_list = object_list.filter(employee__employee_job_informations__department=department)
        if business_unit not in ['', None]:
            object_list = object_list.filter(employee__employee_job_informations__business_unit=business_unit)
        if branch not in ['', None]:
            object_list = object_list.filter(employee__employee_job_informations__branch=branch)
        if schedule not in ['', None]:
            object_list = object_list.filter(employee__employee_attendance__schedule_type=schedule)
        return object_list.order_by('created_at')


class SalaryConfirmationGenerate(LoginRequiredMixin, PermissionMixin, ListView):
    template_name = 'payroll/process/salary_confirmation/list.html'
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

        confirmation_list = EmployeeFilter(employee, from_date, to_date, company, division, department,
                                           business_unit, branch, schedule, ['draft', 'confirmed'])

        if confirmation_list:
            paginator = Paginator(confirmation_list, 50)
            page = self.request.GET.get('page')
            context['confirmation_list'] = paginator.get_page(page)
            index = context['confirmation_list'].number - 1
            max_index = len(paginator.page_range)
            start_index = index - 0 if index >= 3 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            context['page_range'] = list(paginator.page_range)[start_index:end_index]
            context['path'] = "%s" % "&".join(["%s=%s" % (key, value) for (key, value) in self.request.GET.items()
                                               if not key == 'page'])

        context['objects'] = confirmation_list
        return context

    def post(self, request, *args, **kwargs):
        if request.POST:
            employee_salary_id = request.POST.getlist('employee_salary_id')
            for salary in employee_salary_id:
                EmployeeSalary.objects.filter(id=salary).update(status='confirmed')
            messages.success(self.request, "Updated.")
            return redirect('beehive_admin:payroll:salary_confirmation')

        return render(request, self.get_context_data())

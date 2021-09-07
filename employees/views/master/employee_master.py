from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from employees.forms import *
from django.shortcuts import render, redirect, reverse, get_object_or_404
from helpers.mixins import PermissionMixin
from django.contrib import messages
from employees.models import EmployeeIdentification
from helpers.functions import get_organizational_structure


class EmployeeListView(LoginRequiredMixin, PermissionMixin, ListView):
    """
        show all employee list
        Access: Super-Admin, Admin
        Url: /employee/
    """
    template_name = 'employees/master/identification/list.html'
    model = EmployeeIdentification
    permission_required = 'view_employeeidentification'
    context_object_name = 'employee_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        paginator = Paginator(self.object_list, 50)
        page = self.request.GET.get('page')
        context['employee_list'] = paginator.get_page(page)
        index = context['employee_list'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class EmployeeIdentificationCreateView(LoginRequiredMixin, SuccessMessageMixin, PermissionMixin, CreateView):
    """
        Add new employee master identification
        Access: Super-Admin, Admin
        Url: /admin/employees/identification/create
    """
    template_name = 'employees/master/identification/create.html'
    form_class = EmployeeIdentificationForm
    permission_required = 'add_employeeidentification'
    success_message = "Created an employee."

    def get_success_url(self):
        return reverse('employees:employee_identification_update', kwargs={"pk": self.object.pk})


class EmployeeIdentificationUpdateView(LoginRequiredMixin, SuccessMessageMixin, PermissionMixin, UpdateView):
    """
        Change Employee master identification
    """

    model = EmployeeIdentification
    form_class = EmployeeIdentificationForm
    success_message = "Updated Successfully"
    template_name = 'employees/master/identification/update.html'
    success_url = reverse_lazy('employees:employee_identification_update')
    permission_required = 'change_employeeidentification'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.object.pk
        if 'form' not in context:
            context['form'] = self.form_class(self.request.GET)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=self.object)

        if form.is_valid():
            employee = form.save(commit=False)  # just get the form, but don't save to database yet
            employee.is_employee = True
            employee.save()  # save the new employee with information to the database
            messages.success(self.request, "Updated employee.")
            return redirect('employees:employee_identification_update', employee.pk)

        return render(request, self.template_name,
                      {'form': form, 'pk': self.object.pk,
                       'permissions': self.get_current_user_permission_list(),
                       'org_items_list': get_organizational_structure()})


class EmployeeDeleteView(LoginRequiredMixin, PermissionMixin, DeleteView):
    """
        Delete a selected employee
        Access: Super-Admin, Admin
        Url: employees/<pk>/delete
    """
    model = EmployeeIdentification
    template_name = 'employees/master/identification/delete.html'
    success_message = "Deleted successfully."
    success_url = reverse_lazy('employees:employee_master_list')
    permission_required = 'delete_employeeidentification'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.error(self.request, self.success_message % obj.__dict__)
        return super(EmployeeDeleteView, self).delete(request, *args, **kwargs)


class EmployeeJobListView(LoginRequiredMixin, PermissionMixin, ListView):
    template_name = 'employees/master/job/list.html'
    model = emp_models.JobInformation
    permission_required = 'view_jobinformation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']
        job_list = emp_models.JobInformation.objects.filter(employee_id=self.kwargs['pk'])

        paginator = Paginator(job_list, 50)
        page = self.request.GET.get('page')
        context['job_list'] = paginator.get_page(page)
        index = context['job_list'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class EmployeeJobCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Add new employee master job
        Access: Super-Admin, Admin
        Url: /employee/<pk>/job/create
    """
    form_class = EmployeeJobForm
    employment_form_class = EmploymentForm
    contract_form_class = EmploymentContractForm
    separation_form_class = EmploymentSeparationForm
    retirement_form_class = EmploymentRetirementForm
    success_message = "Updated Successfully"
    template_name = 'employees/master/job/create.html'
    permission_required = ['add_jobinformation', 'change_jobinformation', 'view_jobinformation',
                           'delete_jobinformation']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']
        if 'job_id' in self.kwargs:
            get_object_or_404(emp_models.JobInformation, pk=self.kwargs['job_id'])
        if 'job_form' not in context:
            job_info = self.get_job_information()
            if job_info:
                context['job_form'] = self.form_class(instance=job_info)
                # if its 1st job information will show employee form
                if 'job_id' in self.kwargs:
                    first_info = emp_models.JobInformation.objects.filter(employee_id=self.kwargs['pk']).first()
                    if first_info.id == int(self.kwargs['job_id']):
                        context['employment_form'] = self.employment_form_class(
                            instance=emp_models.Employment.objects.filter(employee_id=self.kwargs['pk']).last())
            else:
                context['job_form'] = self.form_class()
                context['employment_form'] = self.employment_form_class()
        if 'contract_form' not in context:
            if self.get_contract_information():
                context['contract_form'] = self.contract_form_class(instance=self.get_contract_information())
            else:
                context['contract_form'] = self.contract_form_class()
        if 'separation_form' not in context:
            if self.get_separation_information():
                context['separation_form'] = self.separation_form_class(instance=self.get_separation_information())
            else:
                context['separation_form'] = self.separation_form_class()
        if 'retirement_form' not in context:
            if self.get_retirement_information():
                context['retirement_form'] = self.retirement_form_class(instance=self.get_retirement_information())
            else:
                context['retirement_form'] = self.retirement_form_class()
        return context

    def get_job_information(self):
        if 'job_id' in self.kwargs:
            data = emp_models.JobInformation.objects.filter(id=self.kwargs['job_id']).last()
        else:
            data = emp_models.JobInformation.objects.filter(employee_id=self.kwargs['pk']).last()
        return data

    def get_contract_information(self):
        contract = emp_models.EndOfContract.objects.filter(employee_id=self.kwargs['pk']).first()
        return contract

    def get_separation_information(self):
        separation = emp_models.Separation.objects.filter(employee_id=self.kwargs['pk']).first()
        return separation

    def get_retirement_information(self):
        retirement = emp_models.Retirement.objects.filter(employee_id=self.kwargs['pk']).first()
        return retirement

    def post(self, request, *args, **kwargs):
        context = dict()
        if 'job_id' in self.kwargs:
            get_object_or_404(emp_models.JobInformation, pk=self.kwargs['job_id'])
        if 'job_form' not in context:
            job_info = self.get_job_information()
            if job_info:
                context['job_form'] = self.form_class(instance=job_info)
                # if its 1st job information will show employee form
                if 'job_id' in self.kwargs:
                    first_info = emp_models.JobInformation.objects.filter(employee_id=self.kwargs['pk']).first()
                    if first_info.id == int(self.kwargs['job_id']):
                        context['employment_form'] = self.employment_form_class(
                            instance=emp_models.Employment.objects.filter(employee_id=self.kwargs['pk']).last())
            else:
                context['job_form'] = self.form_class()
                context['employment_form'] = self.employment_form_class()
        if 'contract_form' not in context:
            if self.get_contract_information():
                context['contract_form'] = self.contract_form_class(instance=self.get_contract_information())
            else:
                context['contract_form'] = self.contract_form_class()
        if 'separation_form' not in context:
            if self.get_separation_information():
                context['separation_form'] = self.separation_form_class(instance=self.get_separation_information())
            else:
                context['separation_form'] = self.separation_form_class()
        if 'retirement_form' not in context:
            if self.get_retirement_information():
                context['retirement_form'] = self.retirement_form_class(instance=self.get_retirement_information())
            else:
                context['retirement_form'] = self.retirement_form_class()
        context['pk'] = self.kwargs['pk']
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        if 'form1' in request.POST:
            if self.get_job_information():
                context['job_form'] = self.form_class(request.POST)
                job_form = context['job_form']
                if job_form.is_valid():
                    if 'job_id' in self.kwargs:
                        if 'confirmation_after' in request.POST:
                            context['employment_form'] = self.employment_form_class(request.POST)
                            employment_form = context['employment_form']
                            if employment_form.is_valid():
                                emp_models.Employment.objects.filter(employee_id=self.kwargs['pk']).update(
                                    confirmation_after=employment_form.cleaned_data['confirmation_after'],
                                    confirmation_after_unit=employment_form.cleaned_data['confirmation_after_unit'],
                                    confirmation_date=employment_form.cleaned_data['confirmation_date'],
                                    date_of_actual_confirmation=employment_form.cleaned_data[
                                        'date_of_actual_confirmation'])
                        updated = emp_models.JobInformation.objects.filter(id=self.kwargs['job_id'],
                                                                           employee_id=self.kwargs['pk']). \
                            update(company=job_form.cleaned_data['company'],
                                   business_unit=job_form.cleaned_data['business_unit'],
                                   division=job_form.cleaned_data['division'],
                                   department=job_form.cleaned_data['department'],
                                   project=job_form.cleaned_data['project'],
                                   designation=job_form.cleaned_data['designation'],
                                   report_to=job_form.cleaned_data['report_to'],
                                   additional_report_to=job_form.cleaned_data['additional_report_to'],
                                   pay_group=job_form.cleaned_data['pay_group'],
                                   pay_scale=job_form.cleaned_data['pay_scale'],
                                   pay_grade=job_form.cleaned_data['pay_grade'],
                                   job_status=job_form.cleaned_data['job_status'],
                                   employment_type=job_form.cleaned_data['employment_type'],
                                   date_of_offer=job_form.cleaned_data['date_of_offer'],
                                   date_of_joining=job_form.cleaned_data['date_of_joining'])
                        messages.success(self.request, "Updated contract information.")
                    else:
                        data, created = emp_models.JobInformation.objects. \
                            get_or_create(employee_id=self.kwargs['pk'], company=job_form.cleaned_data['company'],
                                          business_unit=job_form.cleaned_data['business_unit'],
                                          division=job_form.cleaned_data['division'],
                                          department=job_form.cleaned_data['department'],
                                          project=job_form.cleaned_data['project'],
                                          designation=job_form.cleaned_data['designation'],
                                          report_to=job_form.cleaned_data['report_to'],
                                          additional_report_to=job_form.cleaned_data['additional_report_to'],
                                          pay_group=job_form.cleaned_data['pay_group'],
                                          pay_scale=job_form.cleaned_data['pay_scale'],
                                          pay_grade=job_form.cleaned_data['pay_grade'],
                                          job_status=job_form.cleaned_data['job_status'],
                                          employment_type=job_form.cleaned_data['employment_type'],
                                          date_of_offer=job_form.cleaned_data['date_of_offer'],
                                          date_of_joining=job_form.cleaned_data['date_of_joining'],
                                          defaults={'company': job_form.cleaned_data['company'],
                                                    'business_unit': job_form.cleaned_data['business_unit'],
                                                    'division': job_form.cleaned_data['division'],
                                                    'department': job_form.cleaned_data['department'],
                                                    'project': job_form.cleaned_data['project'],
                                                    'designation': job_form.cleaned_data['designation'],
                                                    'report_to': job_form.cleaned_data['report_to'],
                                                    'additional_report_to': job_form.cleaned_data[
                                                        'additional_report_to'],
                                                    'pay_group': job_form.cleaned_data['pay_group'],
                                                    'pay_scale': job_form.cleaned_data['pay_scale'],
                                                    'pay_grade': job_form.cleaned_data['pay_grade'],
                                                    'job_status': job_form.cleaned_data['job_status'],
                                                    'employment_type': job_form.cleaned_data['employment_type'],
                                                    'date_of_offer': job_form.cleaned_data['date_of_offer'],
                                                    'date_of_joining': job_form.cleaned_data['date_of_joining']})

                        if created:
                            messages.success(self.request, "Created job information.")
                        else:
                            messages.success(self.request, "Already created.")
                    return redirect('employees:employee_job_create', self.kwargs['pk'])

            else:
                context['job_form'] = self.form_class(request.POST)
                job_form = context['job_form']
                context['employment_form'] = self.employment_form_class(request.POST)
                employment_form = context['employment_form']
                if job_form.is_valid() and employment_form.is_valid():
                    job = job_form.save(commit=False)
                    job.employee_id = self.kwargs['pk']
                    job.save()
                    employment = employment_form.save(commit=False)
                    employment.employee_id = self.kwargs['pk']
                    employment.save()
                    messages.success(self.request, "Created job information.")
                    return redirect('employees:employee_job_create', self.kwargs['pk'])

        elif 'form2' in request.POST:
            context['contract_form'] = self.contract_form_class(request.POST)
            contract_form = context['contract_form']
            if contract_form.is_valid() and (
                contract_form.cleaned_data['due_on'] not in EMPTY_VALUES or contract_form.cleaned_data[
                    'date_of_settlement'] not in EMPTY_VALUES or contract_form.cleaned_data[
                    'effective_date'] not in EMPTY_VALUES):
                obj, created = emp_models.EndOfContract.objects.update_or_create(employee_id=self.kwargs['pk'],
                                                                                 defaults={
                                                                                     'due_on':
                                                                                         contract_form.cleaned_data[
                                                                                             'due_on'],
                                                                                     'date_of_settlement':
                                                                                         contract_form.cleaned_data[
                                                                                             'date_of_settlement'],
                                                                                     'effective_date':
                                                                                         contract_form.cleaned_data[
                                                                                             'effective_date']})
                if created:
                    messages.success(self.request, "Created contract information.")
                else:
                    messages.success(self.request, "Updated contract information.")
            else:
                messages.error(self.request, "No data saved.")
            return redirect('employees:employee_job_create', self.kwargs['pk'])
        elif 'form3' in request.POST:
            context['separation_form'] = self.separation_form_class(request.POST)
            separation_form = context['separation_form']
            if separation_form.is_valid():
                if separation_form.cleaned_data['type_of_resign'] == 'sack':
                    date_of_sack = separation_form.cleaned_data['date_of_sack']
                    date_of_resign = None
                    date_of_settlement = separation_form.cleaned_data['date_of_settlement']
                    effective_date = separation_form.cleaned_data['effective_date']
                elif separation_form.cleaned_data['type_of_resign'] == 'resign':
                    date_of_sack = None
                    date_of_resign = separation_form.cleaned_data['date_of_resign']
                    date_of_settlement = separation_form.cleaned_data['date_of_settlement']
                    effective_date = separation_form.cleaned_data['effective_date']
                else:
                    date_of_sack = None
                    date_of_resign = None
                    date_of_settlement = separation_form.cleaned_data['date_of_settlement']
                    effective_date = separation_form.cleaned_data['effective_date']
                obj, created = emp_models.Separation.objects.update_or_create(employee_id=self.kwargs['pk'], defaults={
                    'type_of_resign': separation_form.cleaned_data['type_of_resign'],
                    'date_of_sack': date_of_sack,
                    'date_of_resign': date_of_resign,
                    'date_of_settlement': date_of_settlement,
                    'effective_date': effective_date})
                if created:
                    messages.success(self.request, "Created separation information.")
                else:
                    messages.success(self.request, "Updated separation information.")
                return redirect('employees:employee_job_create', self.kwargs['pk'])
        elif 'form4' in request.POST:
            context['retirement_form'] = self.retirement_form_class(request.POST)
            retirement_form = context['retirement_form']
            if retirement_form.is_valid() and (
                retirement_form.cleaned_data['due_on'] not in EMPTY_VALUES or retirement_form.cleaned_data[
                    'date_of_settlement'] not in EMPTY_VALUES or retirement_form.cleaned_data[
                    'effective_date'] not in EMPTY_VALUES):
                obj, created = emp_models.Retirement.objects.update_or_create(employee_id=self.kwargs['pk'], defaults={
                    'due_on': retirement_form.cleaned_data['due_on'],
                    'date_of_settlement': retirement_form.cleaned_data['date_of_settlement'],
                    'effective_date': retirement_form.cleaned_data['effective_date']})
                if created:
                    messages.success(self.request, "Created retirement information.")
                else:
                    messages.success(self.request, "Updated retirement information.")
            else:
                messages.error(self.request, "No data saved.")
            return redirect('employees:employee_job_create', self.kwargs['pk'])

        return render(request, self.template_name, context)


class EmployeeJobUpdateView(LoginRequiredMixin, PermissionMixin, UpdateView):
    form_class = EmployeeJobForm
    employment_form_class = EmploymentForm
    success_message = "Updated Successfully"
    template_name = 'employees/master/job/update.html'
    permission_required = ['change_jobinformation',]
    model = EmployeeIdentification

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']
        if 'job_id' in self.kwargs:
            get_object_or_404(emp_models.JobInformation, pk=self.kwargs['job_id'])
        if 'job_form' not in context:
            job_info = self.get_job_information()
            if job_info:
                context['job_form'] = self.form_class(instance=job_info)
                # if its 1st job information will show employee form
                if 'job_id' in self.kwargs:
                    first_info = emp_models.JobInformation.objects.filter(employee_id=self.kwargs['pk']).first()
                    if first_info.id == int(self.kwargs['job_id']):
                        context['employment_form'] = self.employment_form_class(
                            instance=emp_models.Employment.objects.filter(employee_id=self.kwargs['pk']).last())
        return context

    def get_job_information(self):
        if 'job_id' in self.kwargs:
            data = emp_models.JobInformation.objects.filter(id=self.kwargs['job_id']).last()
            return data

    def post(self, request, *args, **kwargs):
        context = dict()
        if 'job_id' in self.kwargs:
            get_object_or_404(emp_models.JobInformation, pk=self.kwargs['job_id'])
        if 'job_form' not in context:
            job_info = self.get_job_information()
            if job_info:
                context['job_form'] = self.form_class(instance=job_info)
                # if its 1st job information will show employee form
                if 'job_id' in self.kwargs:
                    first_info = emp_models.JobInformation.objects.filter(employee_id=self.kwargs['pk']).first()
                    if first_info.id == int(self.kwargs['job_id']):
                        context['employment_form'] = self.employment_form_class(
                            instance=emp_models.Employment.objects.filter(employee_id=self.kwargs['pk']).last())
        context['pk'] = self.kwargs['pk']
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        if 'form1' in request.POST:
            if self.get_job_information():
                context['job_form'] = self.form_class(request.POST)
                job_form = context['job_form']
                if job_form.is_valid():
                    if 'job_id' in self.kwargs:
                        if 'confirmation_after' in request.POST:
                            context['employment_form'] = self.employment_form_class(request.POST)
                            employment_form = context['employment_form']
                            if employment_form.is_valid():
                                emp_models.Employment.objects.filter(employee_id=self.kwargs['pk']).update(
                                    confirmation_after=employment_form.cleaned_data['confirmation_after'],
                                    confirmation_after_unit=employment_form.cleaned_data['confirmation_after_unit'],
                                    confirmation_date=employment_form.cleaned_data['confirmation_date'],
                                    date_of_actual_confirmation=employment_form.cleaned_data[
                                        'date_of_actual_confirmation'])
                        emp_models.JobInformation.objects.filter(id=self.kwargs['job_id'],
                                                                           employee_id=self.kwargs['pk']). \
                            update(company=job_form.cleaned_data['company'],
                                   business_unit=job_form.cleaned_data['business_unit'],
                                   division=job_form.cleaned_data['division'],
                                   department=job_form.cleaned_data['department'],
                                   project=job_form.cleaned_data['project'],
                                   designation=job_form.cleaned_data['designation'],
                                   report_to=job_form.cleaned_data['report_to'],
                                   additional_report_to=job_form.cleaned_data['additional_report_to'],
                                   pay_group=job_form.cleaned_data['pay_group'],
                                   pay_scale=job_form.cleaned_data['pay_scale'],
                                   pay_grade=job_form.cleaned_data['pay_grade'],
                                   job_status=job_form.cleaned_data['job_status'],
                                   employment_type=job_form.cleaned_data['employment_type'],
                                   date_of_offer=job_form.cleaned_data['date_of_offer'],
                                   date_of_joining=job_form.cleaned_data['date_of_joining'])
                        messages.success(self.request, self.success_message)
                        return redirect('employees:employee_job_list', self.kwargs['pk'])
        return render(request, self.template_name, context)


class EmployeeJobDeleteView(LoginRequiredMixin, PermissionMixin, DeleteView):
    """
        Delete a selected job information
        Access: Super-Admin, Admin
    """
    model = emp_models.JobInformation
    permission_required = 'delete_jobinformation'
    success_message = "Deleted successfully."

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.error(self.request, self.success_message % obj.__dict__)
        return super(EmployeeJobDeleteView, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('employees:employee_job_create', args=[self.kwargs['employee_pk']])

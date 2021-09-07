from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from employees.forms import *
from django.shortcuts import render, redirect, get_object_or_404
from helpers.mixins import PermissionMixin
from django.contrib import messages
from datetime import date
from helpers.functions import get_organizational_structure


class EmployeePersonalCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Create and update employee personal information
        Access: Super-Admin, Admin
        Url: /employee/<pk>/personal_info/
    """
    form_class = DOBForm
    nationality_form_class = NationalityForm
    tax_form_class = TaxForm
    visa_form_class = VisaForm
    driving_form_class = DrivingForm
    others_form_class = OthersForm
    favourite_form_class = FavouriteForm
    template_name = 'employees/master/personal/create.html'
    permission_required = ['add_personal', 'change_personal', 'view_personal',
                           'delete_personal']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']
        information = self.get_information()
        if 'DOB_form' not in context:
            if information:
                context['DOB_form'] = self.form_class(instance=information)
                if information.date_of_birth is not None:
                    age = self.get_calculate_age(information.date_of_birth)
                    context['years'] = age[0]
                    context['months'] = age[1]
            else:
                context['DOB_form'] = self.form_class()
        if 'nationality_form' not in context:
            if information:
                context['nationality_form'] = self.nationality_form_class(instance=information)
            else:
                context['nationality_form'] = self.nationality_form_class()
        if 'tax_form' not in context:
            if information:
                context['tax_form'] = self.tax_form_class(instance=information)
            else:
                context['tax_form'] = self.tax_form_class()
        if 'visa_form' not in context:
            if information:
                context['visa_form'] = self.visa_form_class(instance=information)
            else:
                context['visa_form'] = self.visa_form_class()
        if 'driving_form' not in context:
            if information:
                context['driving_form'] = self.driving_form_class(instance=information)
            else:
                context['driving_form'] = self.driving_form_class()
        if 'others_form' not in context:
            if information:
                context['others_form'] = self.others_form_class(instance=information)
            else:
                context['others_form'] = self.others_form_class()
        if 'favourite_form' not in context:
            if information:
                context['favourite_form'] = self.favourite_form_class(instance=information)
            else:
                context['favourite_form'] = self.favourite_form_class()
        return context

    def get_information(self):
        data = emp_models.Personal.objects.filter(employee_id=self.kwargs['pk']).first()
        return data

    @staticmethod
    def get_calculate_age(born):
        today = date.today()
        diff = relativedelta(today, born)

        return diff.years, diff.months

    def post(self, request, *args, **kwargs):
        context = dict()
        context['pk'] = self.kwargs['pk']
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        information = self.get_information()
        if 'DOB_form' not in context:
            if information:
                context['DOB_form'] = self.form_class(instance=information)
            else:
                context['DOB_form'] = self.form_class()
        if 'form1' in request.POST:
            context['DOB_form'] = self.form_class(request.POST, request.FILES, instance=information)
            dob_form = context['DOB_form']
            if dob_form.is_valid():
                obj, created = emp_models.Personal.objects.update_or_create(employee_id=self.kwargs['pk'], defaults={
                    'date_of_birth': dob_form.cleaned_data['date_of_birth'],
                    'place_of_birth': dob_form.cleaned_data['place_of_birth'],
                    'birth_certificate': dob_form.cleaned_data['birth_certificate']})
                if created:
                    messages.success(self.request, "Created birth information.")
                else:
                    messages.success(self.request, "Updated birth information.")
                return redirect('employees:employee_personal_info', self.kwargs['pk'])

        if 'nationality_form' not in context:
            if information:
                context['nationality_form'] = self.nationality_form_class(instance=information)
            else:
                context['nationality_form'] = self.nationality_form_class()

        if 'form2' in request.POST:
            context['nationality_form'] = self.nationality_form_class(request.POST, request.FILES,
                                                                      instance=information)
            nationality_form = context['nationality_form']
            if nationality_form.is_valid():
                obj, created = emp_models.Personal.objects.update_or_create(employee_id=self.kwargs['pk'], defaults={
                    'nationality': nationality_form.cleaned_data['nationality'],
                    'passport_number': nationality_form.cleaned_data['passport_number'],
                    'nid_or_ssn_number': nationality_form.cleaned_data['nid_or_ssn_number'],
                    'passport_expiry_date': nationality_form.cleaned_data['passport_expiry_date'],
                    'nid': nationality_form.cleaned_data['nid'],
                    'passport': nationality_form.cleaned_data['passport']})
                if created:
                    messages.success(self.request, "Created nationality and passport information.")
                else:
                    messages.success(self.request, "Updated nationality and passport information.")
                return redirect('employees:employee_personal_info', self.kwargs['pk'])

        if 'tax_form' not in context:
            if information:
                context['tax_form'] = self.tax_form_class(instance=information)
            else:
                context['tax_form'] = self.tax_form_class()

        if 'form3' in request.POST:
            context['tax_form'] = self.tax_form_class(request.POST, request.FILES, instance=information)
            tax_form = context['tax_form']
            if tax_form.is_valid():
                obj, created = emp_models.Personal.objects.update_or_create(employee_id=self.kwargs['pk'], defaults={
                    'tin_number': tax_form.cleaned_data['tin_number'],
                    'TIN': tax_form.cleaned_data['TIN']})
                if created:
                    messages.success(self.request, "Created tax information.")
                else:
                    messages.success(self.request, "Updated tax information.")
                return redirect('employees:employee_personal_info', self.kwargs['pk'])

        if 'visa_form' not in context:
            if information:
                context['visa_form'] = self.visa_form_class(instance=information)
            else:
                context['visa_form'] = self.visa_form_class()

        if 'form4' in request.POST:
            context['visa_form'] = self.visa_form_class(request.POST, request.FILES, instance=information)
            visa_form = context['visa_form']
            if visa_form.is_valid():
                obj, created = emp_models.Personal.objects.update_or_create(employee_id=self.kwargs['pk'], defaults={
                    'visa_type': visa_form.cleaned_data['visa_type'],
                    'visa_number': visa_form.cleaned_data['visa_number'],
                    'work_permit_no': visa_form.cleaned_data['work_permit_no'],
                    'work_permit_expiry_date': visa_form.cleaned_data['work_permit_expiry_date'],
                    'work_permit_doc': visa_form.cleaned_data['work_permit_doc']})
                if created:
                    messages.success(self.request, "Created visa and work permit information.")
                else:
                    messages.success(self.request, "Updated visa and work permit information.")
                return redirect('employees:employee_personal_info', self.kwargs['pk'])

        if 'driving_form' not in context:
            if information:
                context['driving_form'] = self.driving_form_class(instance=information)
            else:
                context['driving_form'] = self.driving_form_class()

        if 'form5' in request.POST:
            context['driving_form'] = self.driving_form_class(request.POST, request.FILES,
                                                              instance=information)
            driving_form = context['driving_form']
            if driving_form.is_valid():
                obj, created = emp_models.Personal.objects.update_or_create(employee_id=self.kwargs['pk'], defaults={
                    'driving_licence_no': driving_form.cleaned_data['driving_licence_no'],
                    'driving_licence_expiry_date': driving_form.cleaned_data['driving_licence_expiry_date'],
                    'driving_licence_doc': driving_form.cleaned_data['driving_licence_doc']})
                if created:
                    messages.success(self.request, "Created driving information.")
                else:
                    messages.success(self.request, "Updated driving information.")
                return redirect('employees:employee_personal_info', self.kwargs['pk'])

        if 'others_form' not in context:
            if information:
                context['others_form'] = self.others_form_class(instance=information)
            else:
                context['others_form'] = self.others_form_class()

        if 'form6' in request.POST:
            context['others_form'] = self.others_form_class(request.POST, request.FILES,
                                                            instance=information)
            others_form = context['others_form']
            if others_form.is_valid():
                obj, created = emp_models.Personal.objects.update_or_create(employee_id=self.kwargs['pk'], defaults={
                    'mothers_name': others_form.cleaned_data['mothers_name'],
                    'fathers_name': others_form.cleaned_data['fathers_name'],
                    'marital_status': others_form.cleaned_data['marital_status'],
                    'spouse_name': others_form.cleaned_data['spouse_name'],
                    'no_of_child': others_form.cleaned_data['no_of_child'],
                    'height_ft': others_form.cleaned_data['height_ft'],
                    'height_in': others_form.cleaned_data['height_in'],
                    'weight': others_form.cleaned_data['weight'],
                    'weight_unit': others_form.cleaned_data['weight_unit'],
                    'blood_group': others_form.cleaned_data['blood_group'],
                    'identification_mark': others_form.cleaned_data['identification_mark'],
                    'religion': others_form.cleaned_data['religion'],
                    'caste': others_form.cleaned_data['caste'],
                    'mother_tongue': others_form.cleaned_data['mother_tongue'],
                    'police_station_address': others_form.cleaned_data['police_station_address'],
                    'fingerprint': others_form.cleaned_data['fingerprint'],
                    'signature': others_form.cleaned_data['signature']})
                if created:
                    messages.success(self.request, "Created others information.")
                else:
                    messages.success(self.request, "Updated others information.")
                return redirect('employees:employee_personal_info', self.kwargs['pk'])

        if 'favourite_form' not in context:
            if information:
                context['favourite_form'] = self.favourite_form_class(instance=information)
            else:
                context['favourite_form'] = self.favourite_form_class()

        if 'form7' in request.POST:
            context['favourite_form'] = self.favourite_form_class(request.POST, request.FILES,
                                                                  instance=information)
            favourite_form = context['favourite_form']
            if favourite_form.is_valid():
                obj, created = emp_models.Personal.objects.update_or_create(employee_id=self.kwargs['pk'], defaults={
                    'preferred_food': favourite_form.cleaned_data['preferred_food'],
                    'hobby': favourite_form.cleaned_data['hobby']})
                if created:
                    messages.success(self.request, "Created favourite information.")
                else:
                    messages.success(self.request, "Updated favourite information.")
                return redirect('employees:employee_personal_info', self.kwargs['pk'])

        return render(request, self.template_name, context)

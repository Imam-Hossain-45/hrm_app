from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from employees.forms import *
from django.shortcuts import render, redirect, get_object_or_404
from helpers.mixins import PermissionMixin
from django.contrib import messages
from django.forms import modelformset_factory
from django.utils.html import format_html
from helpers.functions import get_organizational_structure


class EmployeeContactCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Create and update employee address and contact information
        Access: Super-Admin, Admin
        Url: /employee/<pk>/address_&_contact/
    """
    form_class = ContactForm
    email_form_class = EmailForm
    address_form_class = AddressForm
    emergency_form_class = EmergencyContactForm
    template_name = 'employees/master/contact/create.html'
    permission_required = ['add_addressandcontact', 'change_addressandcontact', 'view_addressandcontact',
                           'delete_addressandcontact']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']
        info = self.get_information()
        if 'contact_form' not in context:
            if info:
                context['contact_form'] = self.form_class(instance=info)
            else:
                context['contact_form'] = self.form_class()
        if 'email_form' not in context:
            if info:
                context['email_form'] = self.email_form_class(instance=info)
            else:
                context['email_form'] = self.email_form_class()
        if 'address_form' not in context:
            if info:
                address_form = self.address_form_class(instance=info)
                context['address_form'] = address_form
                context['present_state'] = address_form['present_state']
                context['present_city'] = address_form['present_city']
                context['permanent_state'] = address_form['permanent_state']
                context['permanent_city'] = address_form['permanent_city']
            else:
                context['address_form'] = self.address_form_class()
        if 'emergency_form' not in context:
            emergencyformset = modelformset_factory(emp_models.EmergencyContact, form=EmergencyContactForm, extra=1,
                                                    can_delete=True)
            context['emergency_form'] = emergencyformset(queryset=self.get_emergency_information())
        return context

    def render_to_response(self, context, **response_kwargs):
        """ Allow AJAX requests to be handled more gracefully """
        if self.request.is_ajax():
            present_country_id = self.request.GET.get('present_country_id')
            present_state_id = self.request.GET.get('present_state_id')
            permanent_country_id = self.request.GET.get('permanent_country_id')
            permanent_state_id = self.request.GET.get('permanent_state_id')

            if present_country_id not in EMPTY_VALUES:
                present_state = []
                present_state.append(format_html("<option value=''>-------</option>"))
                for pre_state in States.objects.filter(country_id=present_country_id):
                    present_state.append(format_html(
                        str("<option value=") + str(pre_state.id) + str(">") + pre_state.name + str("</option>")))
                return render(self.request, 'employees/master/contact/present_state.html',
                              {'present_state': present_state})
            elif present_state_id not in EMPTY_VALUES:
                present_city = []
                present_city.append(format_html("<option value=''>-------</option>"))
                for pre_city in Cities.objects.filter(state_id=present_state_id):
                    present_city.append(format_html(
                        str("<option value=") + str(pre_city.id) + str(">") + pre_city.name + str("</option>")))
                return render(self.request, 'employees/master/contact/present_city.html',
                              {'present_city': present_city})
            elif permanent_country_id not in EMPTY_VALUES:
                permanent_state = []
                permanent_state.append(format_html("<option value=''>-------</option>"))
                for per_state in States.objects.filter(country_id=permanent_country_id):
                    permanent_state.append(format_html(
                        str("<option value=") + str(per_state.id) + str(">") + per_state.name + str("</option>")))
                return render(self.request, 'employees/master/contact/permanent_state.html',
                              {'permanent_state': permanent_state})
            elif permanent_state_id not in EMPTY_VALUES:
                permanent_city = []
                permanent_city.append(format_html("<option value=''>-------</option>"))
                for per_city in Cities.objects.filter(state_id=permanent_state_id):
                    permanent_city.append(format_html(
                        str("<option value=") + str(per_city.id) + str(">") + per_city.name + str("</option>")))
                return render(self.request, 'employees/master/contact/permanent_city.html',
                              {'permanent_city': permanent_city})
            else:
                return render(self.request, 'employees/master/contact/address_form.html')
        else:
            return super(CreateView, self).render_to_response(context, **response_kwargs)

    def get_information(self):
        data = emp_models.AddressAndContact.objects.filter(employee_id=self.kwargs['pk']).last()
        return data

    def get_emergency_information(self):
        data = emp_models.EmergencyContact.objects.filter(employee_id=self.kwargs['pk'])
        return data

    def post(self, request, *args, **kwargs):
        context = dict()
        context['pk'] = self.kwargs['pk']
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        if 'contact_form' not in context:
            if self.get_information():
                context['contact_form'] = self.form_class(instance=self.get_information())
            else:
                context['contact_form'] = self.form_class()
        if 'form1' in request.POST:
            context['contact_form'] = self.form_class(request.POST, instance=self.get_information())
            contact_form = context['contact_form']
            if contact_form.is_valid():
                obj, created = emp_models.AddressAndContact.objects.update_or_create(employee_id=self.kwargs['pk'],
                                                                                     defaults={
                                                                                         'official_cell_number':
                                                                                             contact_form.cleaned_data[
                                                                                                 'official_cell_number'],
                                                                                         'personal_cell_number':
                                                                                             contact_form.cleaned_data[
                                                                                                 'personal_cell_number']})
                if created:
                    messages.success(self.request, "Created contact information.")
                else:
                    messages.success(self.request, "Updated contact information.")
                return redirect('employees:employee_contact_info', self.kwargs['pk'])

        if 'email_form' not in context:
            if self.get_information():
                context['email_form'] = self.email_form_class(instance=self.get_information())
            else:
                context['email_form'] = self.email_form_class()

        if 'form2' in request.POST:
            context['email_form'] = self.email_form_class(request.POST, instance=self.get_information())
            email_form = context['email_form']
            if email_form.is_valid():
                obj, created = emp_models.AddressAndContact.objects.update_or_create(employee_id=self.kwargs['pk'],
                                                                                     defaults={
                                                                                         'official_email_ID':
                                                                                             email_form.cleaned_data[
                                                                                                 'official_email_ID'],
                                                                                         'personal_email_ID':
                                                                                             email_form.cleaned_data[
                                                                                                 'personal_email_ID']})
                if created:
                    messages.success(self.request, "Created email and passport information.")
                else:
                    messages.success(self.request, "Updated email and passport information.")
                return redirect('employees:employee_contact_info', self.kwargs['pk'])

        if 'address_form' not in context:
            if self.get_information():
                context['address_form'] = self.address_form_class(instance=self.get_information())
            else:
                context['address_form'] = self.address_form_class()

        if 'form4' in request.POST:
            context['address_form'] = self.address_form_class(request.POST, instance=self.get_information())
            address_form = context['address_form']
            context['address_form'] = address_form
            context['present_state'] = address_form['present_state']
            context['present_city'] = address_form['present_city']
            context['permanent_state'] = address_form['permanent_state']
            context['permanent_city'] = address_form['permanent_city']
            if address_form.is_valid():
                obj, created = emp_models.AddressAndContact.objects. \
                    update_or_create(employee_id=self.kwargs['pk'],
                                     defaults={'present_address': address_form.cleaned_data['present_address'],
                                               'present_country': address_form.cleaned_data['present_country'],
                                               'present_state': address_form.cleaned_data['present_state'],
                                               'present_city': address_form.cleaned_data['present_city'],
                                               'present_thana': address_form.cleaned_data['present_thana'],
                                               'present_postal_code': address_form.cleaned_data['present_postal_code'],
                                               'present_contact_person': address_form.cleaned_data[
                                                   'present_contact_person'],
                                               'present_phone_number': address_form.cleaned_data[
                                                   'present_phone_number'],
                                               'permanent_address': address_form.cleaned_data['permanent_address'],
                                               'permanent_country': address_form.cleaned_data['permanent_country'],
                                               'permanent_city': address_form.cleaned_data['permanent_city'],
                                               'permanent_state': address_form.cleaned_data['permanent_state'],
                                               'permanent_thana': address_form.cleaned_data['permanent_thana'],
                                               'permanent_postal_code': address_form.cleaned_data[
                                                   'permanent_postal_code'],
                                               'permanent_contact_person': address_form.cleaned_data[
                                                   'permanent_contact_person'],
                                               'permanent_phone_number': address_form.cleaned_data[
                                                   'permanent_phone_number']})
                if created:
                    messages.success(self.request, "Created address information.")
                else:
                    messages.success(self.request, "Updated address information.")
                return redirect('employees:employee_contact_info', self.kwargs['pk'])

        if 'emergency_form' not in context:
            EmergencyFormSet = modelformset_factory(emp_models.EmergencyContact, form=EmergencyContactForm, extra=1,
                                                    can_delete=True)
            context['emergency_form'] = EmergencyFormSet(queryset=self.get_emergency_information())

        if 'form3' in request.POST:
            EmergencyFormSet = modelformset_factory(emp_models.EmergencyContact, form=EmergencyContactForm, extra=1,
                                                    can_delete=True, min_num=1, validate_min=True)
            data = {
                'form-TOTAL_FORMS': request.POST['form-TOTAL_FORMS'],
                'form-INITIAL_FORMS': request.POST['form-INITIAL_FORMS'],
                'form-MIN_NUM_FORMS': request.POST['form-MIN_NUM_FORMS'],
            }
            for i in range(int(data['form-TOTAL_FORMS'])):
                data['form-' + str(i) + '-name'] = request.POST['form-' + str(i) + '-name']
                data['form-' + str(i) + '-relationship'] = request.POST['form-' + str(i) + '-relationship']
                data['form-' + str(i) + '-address'] = request.POST['form-' + str(i) + '-address']
                data['form-' + str(i) + '-contact'] = request.POST['form-' + str(i) + '-contact_0'] + ':::' + \
                                                      request.POST['form-' + str(i) + '-contact_1']
                data['form-' + str(i) + '-email'] = request.POST['form-' + str(i) + '-email']
                if request.POST.get('form-' + str(i) + '-DELETE'):
                    data['form-' + str(i) + '-DELETE'] = request.POST['form-' + str(i) + '-DELETE']
                else:
                    data['form-' + str(i) + '-DELETE'] = ''
            context['emergency_form'] = EmergencyFormSet(request.POST, data)
            emergency_form = context['emergency_form']
            if emergency_form.is_valid():
                for emergency in emergency_form:
                    forms = emergency_form.save(commit=False)
                    for object in emergency_form.deleted_objects:
                        object.delete()
                    if emergency.cleaned_data.get('name') is not None:
                        em = emergency.save(commit=False)
                        em.contact = emergency.cleaned_data.get('contact')
                        em.employee_id = self.kwargs['pk']
                        emergency.save()
                messages.success(self.request, "Updated emergency contact information.")
                return redirect('employees:employee_contact_info', self.kwargs['pk'])

        return render(request, self.template_name, context)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import CreateView, DeleteView, ListView
from django.urls import reverse_lazy
from employees.forms import *
from django.shortcuts import render, redirect, get_object_or_404
from helpers.mixins import PermissionMixin
from django.contrib import messages
from django.utils.html import format_html
from helpers.functions import get_organizational_structure


class ReferenceListView(LoginRequiredMixin, PermissionMixin, ListView):
    template_name = 'employees/master/reference/list.html'
    model = emp_models.Reference
    permission_required = 'view_reference'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']
        reference_list = emp_models.Reference.objects.filter(employee_id=self.kwargs['pk'])

        paginator = Paginator(reference_list, 50)
        page = self.request.GET.get('page')
        context['reference_list'] = paginator.get_page(page)
        index = context['reference_list'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class ReferenceCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Add new employee master reference
        Access: Super-Admin, Admin
        Url: /employee/<pk>/reference/create
    """
    form_class = ReferenceForm
    template_name = 'employees/master/reference/create.html'
    permission_required = ['add_reference', 'change_reference', 'view_reference',
                           'delete_reference']

    def get_queryset(self):
        return emp_models.Reference.objects.filter(employee_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']
        info = self.get_information()
        if 'reference_id' in self.kwargs:
            get_object_or_404(emp_models.Reference, pk=self.kwargs['reference_id'])
        if 'ref_form' not in context:
            if info:
                ref_form = self.form_class(instance=info)
                context['ref_form'] = ref_form
                context['states'] = ref_form['state']
                context['cities'] = ref_form['city']
            else:
                context['ref_form'] = self.form_class()
        context['object_list'] = self.get_queryset()
        return context

    def render_to_response(self, context, **response_kwargs):
        """ Allow AJAX requests to be handled more gracefully """
        if self.request.is_ajax():
            country_id = self.request.GET.get('country_id')
            state_id = self.request.GET.get('state_id')

            if country_id not in EMPTY_VALUES:
                states = []
                states.append(format_html("<option value=''>-------</option>"))
                for pre_state in States.objects.filter(country_id=country_id):
                    states.append(format_html(
                        str("<option value=") + str(pre_state.id) + str(">") + pre_state.name + str("</option>")))
                return render(self.request, 'employees/master/reference/states.html',
                              {'states': states})
            elif state_id not in EMPTY_VALUES:
                cities = []
                cities.append(format_html("<option value=''>-------</option>"))
                for pre_city in Cities.objects.filter(state_id=state_id):
                    cities.append(format_html(
                        str("<option value=") + str(pre_city.id) + str(">") + pre_city.name + str("</option>")))
                return render(self.request, 'employees/master/reference/cities.html',
                              {'cities': cities})
            else:
                return render(self.request, 'employees/master/reference/form.html')
        else:
            return super(CreateView, self).render_to_response(context, **response_kwargs)

    def get_information(self):
        if 'reference_id' in self.kwargs:
            data = emp_models.Reference.objects.filter(id=self.kwargs['reference_id']).last()
        else:
            data = emp_models.Reference.objects.filter(employee_id=self.kwargs['pk']).last()
        return data

    def post(self, request, *args, **kwargs):
        context = dict()
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        info = self.get_information()
        if info:
            ref_form = self.form_class(request.POST, instance=info)
        else:
            ref_form = self.form_class(request.POST)
        context['ref_form'] = ref_form
        context['states'] = ref_form['state']
        context['cities'] = ref_form['city']
        context['pk'] = self.kwargs['pk']
        context['object_list'] = self.get_queryset()
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        print(ref_form.errors)
        if ref_form.is_valid():
            if 'reference_id' in self.kwargs:
                updated = emp_models.Reference.objects.filter(id=self.kwargs['reference_id'],
                                                              employee_id=self.kwargs['pk']). \
                    update(ref_person_name=ref_form.cleaned_data['ref_person_name'],
                           relationship=ref_form.cleaned_data['relationship'],
                           designation=ref_form.cleaned_data['designation'],
                           official_cell_number=ref_form.cleaned_data['official_cell_number'],
                           personal_cell_number=ref_form.cleaned_data['personal_cell_number'],
                           official_email=ref_form.cleaned_data['official_email'],
                           personal_email=ref_form.cleaned_data['personal_email'],
                           organization_name=ref_form.cleaned_data['organization_name'],
                           address_line=ref_form.cleaned_data['address_line'],
                           country=ref_form.cleaned_data['country'],
                           state=ref_form.cleaned_data['state'],
                           city=ref_form.cleaned_data['city'],
                           thana=ref_form.cleaned_data['thana'],
                           postal_code=ref_form.cleaned_data['postal_code'],
                           contact_person=ref_form.cleaned_data['contact_person'],
                           phone_number=ref_form.cleaned_data['phone_number'])
                messages.success(self.request, "Updated reference.")
                return redirect('employees:employee_reference_list', self.kwargs['pk'])
            else:
                data, created = emp_models.Reference.objects. \
                    get_or_create(employee_id=self.kwargs['pk'],
                                  ref_person_name=ref_form.cleaned_data['ref_person_name'],
                                  relationship=ref_form.cleaned_data['relationship'],
                                  designation=ref_form.cleaned_data['designation'],
                                  official_cell_number=ref_form.cleaned_data['official_cell_number'],
                                  personal_cell_number=ref_form.cleaned_data['personal_cell_number'],
                                  official_email=ref_form.cleaned_data['official_email'],
                                  personal_email=ref_form.cleaned_data['personal_email'],
                                  organization_name=ref_form.cleaned_data['organization_name'],
                                  address_line=ref_form.cleaned_data['address_line'],
                                  country=ref_form.cleaned_data['country'],
                                  state=ref_form.cleaned_data['state'],
                                  city=ref_form.cleaned_data['city'],
                                  thana=ref_form.cleaned_data['thana'],
                                  postal_code=ref_form.cleaned_data['postal_code'],
                                  contact_person=ref_form.cleaned_data['contact_person'],
                                  phone_number=ref_form.cleaned_data['phone_number'],
                                  defaults={'ref_person_name': ref_form.cleaned_data['ref_person_name'],
                                            'relationship': ref_form.cleaned_data['relationship'],
                                            'designation': ref_form.cleaned_data['designation'],
                                            'official_cell_number': ref_form.cleaned_data['official_cell_number'],
                                            'personal_cell_number': ref_form.cleaned_data['personal_cell_number'],
                                            'official_email': ref_form.cleaned_data['official_email'],
                                            'personal_email': ref_form.cleaned_data['personal_email'],
                                            'organization_name': ref_form.cleaned_data[
                                                'organization_name'],
                                            'address_line': ref_form.cleaned_data['address_line'],
                                            'country': ref_form.cleaned_data['country'],
                                            'state': ref_form.cleaned_data['state'],
                                            'city': ref_form.cleaned_data['city'],
                                            'thana': ref_form.cleaned_data['thana'],
                                            'postal_code': ref_form.cleaned_data['postal_code'],
                                            'contact_person': ref_form.cleaned_data['contact_person'],
                                            'phone_number': ref_form.cleaned_data['phone_number']})

                if created:
                    messages.success(self.request, "Created reference.")
                else:
                    messages.success(self.request, "Already created.")
            return redirect('employees:employee_reference_create', self.kwargs['pk'])

        return render(request, self.template_name, context)


class ReferenceDeleteView(LoginRequiredMixin, PermissionMixin, DeleteView):
    """
        Delete a selected reference
        Access: Super-Admin, Admin
    """
    model = emp_models.Reference
    permission_required = 'delete_reference'
    success_message = "Deleted"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(ReferenceDeleteView, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('employees:employee_reference_create', args=[self.kwargs['employee_pk']])

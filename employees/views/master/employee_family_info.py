from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import CreateView
from employees.forms import *
from django.shortcuts import render, redirect, get_object_or_404
from helpers.mixins import PermissionMixin
from django.contrib import messages
from django.forms import modelformset_factory
from helpers.functions import get_organizational_structure


class EmployeeFamilyCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Create and update employee family information
        Access: Super-Admin, Admin
        Url: /employee/<pk>/family/
    """
    form_class = FamilyForm
    template_name = 'employees/master/family/create.html'
    permission_required = ['add_family', 'change_family', 'view_family',
                           'delete_family']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']
        information = self.get_information()

        if information.count() > 0:
            familyformset = modelformset_factory(emp_models.Family, form=FamilyForm,
                                                 extra=0, can_delete=True)

            paginator = Paginator(information, 50)
            page = self.request.GET.get('page')
            family_page_list = paginator.get_page(page)
            family_page_list.ordered = True
            index = family_page_list.number - 1
            max_index = len(paginator.page_range)
            start_index = index - 0 if index >= 3 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            context['page_range'] = list(paginator.page_range)[start_index:end_index]

            page_query = information.filter(id__in=[object.id for object in family_page_list])
            context['objects'] = family_page_list
            context['family_form'] = familyformset(queryset=page_query)

        else:
            familyformset = modelformset_factory(emp_models.Family, form=FamilyForm,
                                                 extra=1, can_delete=True)
            context['family_form'] = familyformset(queryset=information)

        return context

    def get_information(self):
        data = emp_models.Family.objects.filter(employee_id=self.kwargs['pk'])
        return data

    def post(self, request, *args, **kwargs):
        context = dict()
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['pk'] = self.kwargs['pk']
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        information = self.get_information()

        if information.count() > 0:
            familyformset = modelformset_factory(emp_models.Family, form=FamilyForm,
                                                 extra=0, can_delete=True)

            paginator = Paginator(information, 50)
            page = self.request.GET.get('page')
            family_page_list = paginator.get_page(page)
            family_page_list.ordered = True
            index = family_page_list.number - 1
            max_index = len(paginator.page_range)
            start_index = index - 0 if index >= 3 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            context['page_range'] = list(paginator.page_range)[start_index:end_index]

            page_query = information.filter(id__in=[object.id for object in family_page_list])
            context['objects'] = family_page_list
            context['family_form'] = familyformset(queryset=page_query)

        else:
            familyformset = modelformset_factory(emp_models.Family, form=FamilyForm,
                                                 extra=1, can_delete=True)
            context['family_form'] = familyformset(queryset=information)

        if 'form1' in request.POST:
            familyFormSet = modelformset_factory(emp_models.Family, form=FamilyForm, extra=1, can_delete=True, min_num=1, validate_min=True)
            data = {
                'form-TOTAL_FORMS': request.POST['form-TOTAL_FORMS'],
                'form-INITIAL_FORMS': request.POST['form-INITIAL_FORMS'],
                'form-MIN_NUM_FORMS': request.POST['form-MIN_NUM_FORMS'],
            }
            for i in range(int(data['form-TOTAL_FORMS'])):
                data['form-'+str(i)+'-name_of_family_member'] = request.POST['form-'+str(i)+'-name_of_family_member']
                data['form-'+str(i)+'-relationship_with_employee'] = request.POST['form-'+str(i)+'-relationship_with_employee']
                data['form-'+str(i)+'-DOB'] = request.POST['form-'+str(i)+'-DOB']
                data['form-'+str(i)+'-age'] = request.POST['form-'+str(i)+'-age']
                data['form-'+str(i)+'-gender'] = request.POST['form-'+str(i)+'-gender']
                data['form-'+str(i)+'-employed'] = request.POST['form-'+str(i)+'-employed']
                data['form-'+str(i)+'-dependent'] = request.POST['form-'+str(i)+'-dependent']
                if request.POST.get('form-'+str(i)+'-DELETE'):
                    data['form-' + str(i) + '-DELETE'] = request.POST['form-' + str(i) + '-DELETE']
                else:
                    data['form-' + str(i) + '-DELETE'] = ''
            context['family_form'] = familyFormSet(request.POST, data)
            family_form = context['family_form']
            if family_form.is_valid():
                for family in family_form:
                    family_form.save(commit=False)
                    for object in family_form.deleted_objects:
                        object.delete()
                    if family.cleaned_data.get('name_of_family_member') is not None:
                        em = family.save(commit=False)
                        em.employee_id = self.kwargs['pk']
                        family.save()
                messages.success(self.request, "Updated family information.")
                return redirect('employees:employee_family_info', self.kwargs['pk'])

        return render(request, self.template_name, context)

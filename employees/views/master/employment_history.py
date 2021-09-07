from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import CreateView
from employees.forms import *
from django.shortcuts import render, redirect, get_object_or_404
from helpers.mixins import PermissionMixin
from django.contrib import messages
from django.forms import modelformset_factory
from helpers.functions import get_organizational_structure


class EmploymentHistoryCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Create and update employee family information
        Access: Super-Admin, Admin
        Url: /employee/<pk>/previous_employment/
    """
    form_class = EmploymentHistoryForm
    template_name = 'employees/master/previous_employment/create.html'
    permission_required = ['add_employmenthistory', 'change_employmenthistory', 'view_employmenthistory',
                           'delete_employmenthistory']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']
        information = self.get_information()

        if information.count() > 0:
            historyformset = modelformset_factory(emp_models.EmploymentHistory, form=EmploymentHistoryForm, extra=0,
                                                  can_delete=True)

            paginator = Paginator(information, 50)
            page = self.request.GET.get('page')
            employment_page_list = paginator.get_page(page)
            employment_page_list.ordered = True
            index = employment_page_list.number - 1
            max_index = len(paginator.page_range)
            start_index = index - 0 if index >= 3 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            context['page_range'] = list(paginator.page_range)[start_index:end_index]

            page_query = information.filter(id__in=[object.id for object in employment_page_list])
            context['objects'] = employment_page_list
            context['previous_employment_form'] = historyformset(queryset=page_query)

        else:
            historyformset = modelformset_factory(emp_models.EmploymentHistory, form=EmploymentHistoryForm, extra=1,
                                                  can_delete=True)
            context['previous_employment_form'] = historyformset(queryset=information)

        return context

    def get_information(self):
        data = emp_models.EmploymentHistory.objects.filter(employee_id=self.kwargs['pk']).order_by('-id')
        return data

    def post(self, request, *args, **kwargs):
        context = dict()
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['pk'] = self.kwargs['pk']
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        information = self.get_information()

        if information.count() > 0:
            historyformset = modelformset_factory(emp_models.EmploymentHistory, form=EmploymentHistoryForm, extra=0,
                                                  can_delete=True)

            paginator = Paginator(information, 50)
            page = self.request.GET.get('page')
            employment_page_list = paginator.get_page(page)
            employment_page_list.ordered = True
            index = employment_page_list.number - 1
            max_index = len(paginator.page_range)
            start_index = index - 0 if index >= 3 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            context['page_range'] = list(paginator.page_range)[start_index:end_index]

            page_query = information.filter(id__in=[object.id for object in employment_page_list])
            context['objects'] = employment_page_list
            context['previous_employment_form'] = historyformset(queryset=page_query)

        else:
            historyformset = modelformset_factory(emp_models.EmploymentHistory, form=EmploymentHistoryForm, extra=1,
                                                  can_delete=True)
            context['previous_employment_form'] = historyformset(queryset=information)

        if 'form1' in request.POST:

            historyformset = modelformset_factory(emp_models.EmploymentHistory, form=EmploymentHistoryForm, extra=1,
                                                  can_delete=True, min_num=1, validate_min=True)

            data = {
                'form-TOTAL_FORMS': request.POST['form-TOTAL_FORMS'],
                'form-INITIAL_FORMS': request.POST['form-INITIAL_FORMS'],
                'form-MIN_NUM_FORMS': request.POST['form-MIN_NUM_FORMS'],
            }

            for i in range(int(data['form-TOTAL_FORMS'])):
                data['form-' + str(i) + '-organization'] = request.POST['form-' + str(i) + '-organization']
                data['form-' + str(i) + '-designation'] = request.POST['form-' + str(i) + '-designation']
                data['form-' + str(i) + '-department'] = request.POST['form-' + str(i) + '-department']
                data['form-' + str(i) + '-start_from'] = request.POST['form-' + str(i) + '-start_from']
                data['form-' + str(i) + '-to'] = request.POST['form-' + str(i) + '-to']
                data['form-' + str(i) + '-salary'] = request.POST['form-' + str(i) + '-salary']
                if request.POST.get('form-' + str(i) + '-DELETE'):
                    data['form-' + str(i) + '-DELETE'] = request.POST['form-' + str(i) + '-DELETE']
                else:
                    data['form-' + str(i) + '-DELETE'] = ''

            context['previous_employment_form'] = historyformset(request.POST, data)
            previous_employment_form = context['previous_employment_form']

            if previous_employment_form.is_valid():
                for history in previous_employment_form:
                    previous_employment_form.save(commit=False)
                    for object in previous_employment_form.deleted_objects:
                        object.delete()
                    if history.cleaned_data.get('organization') is not None:
                        em = history.save(commit=False)
                        em.employee_id = self.kwargs['pk']
                        history.save()
                messages.success(self.request, "Updated employment history.")
                return redirect('employees:employment_history', self.kwargs['pk'])

        return render(request, self.template_name, context)

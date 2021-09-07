from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import CreateView, DeleteView, ListView
from django.urls import reverse_lazy
from employees.forms import *
from django.shortcuts import render, redirect, get_object_or_404
from helpers.mixins import PermissionMixin
from django.contrib import messages
from django.db import IntegrityError
from helpers.functions import get_organizational_structure


class EducationListView(LoginRequiredMixin, PermissionMixin, ListView):
    template_name = 'employees/master/education/list.html'
    model = emp_models.Education
    permission_required = 'view_education'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']
        education_list = emp_models.Education.objects.filter(employee_id=self.kwargs['pk'])

        paginator = Paginator(education_list, 50)
        page = self.request.GET.get('page')
        context['education_list'] = paginator.get_page(page)
        index = context['education_list'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class EducationCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Add new Education qualification
        Access: Super-Admin, Admin
        Url: /employee/<pk>/education/create
    """
    form_class = EducationForm
    template_name = 'employees/master/education/create.html'
    permission_required = ['add_education', 'change_education', 'view_education',
                           'delete_education']

    def get_queryset(self):
        return emp_models.Education.objects.filter(employee_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']
        if 'education_id' in self.kwargs:
            get_object_or_404(emp_models.Education, pk=self.kwargs['education_id'])
        if 'education_form' not in context:
            if self.get_information():
                context['education_form'] = self.form_class(instance=self.get_information())
            else:
                context['education_form'] = self.form_class()
        context['object_list'] = self.get_queryset()
        return context

    def get_information(self):
        if 'education_id' in self.kwargs:
            data = emp_models.Education.objects.filter(id=self.kwargs['education_id']).last()
        else:
            data = emp_models.Education.objects.filter(employee_id=self.kwargs['pk']).last()
        return data

    def post(self, request, *args, **kwargs):
        context = dict()
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        if 'education_form' not in context:
            if self.get_information():
                context['education_form'] = self.form_class(instance=self.get_information())
            else:
                context['education_form'] = self.form_class()
        context['pk'] = self.kwargs['pk']
        context['object_list'] = self.get_queryset()
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        if 'form1' in request.POST:
            context['education_form'] = self.form_class(request.POST, request.FILES or None,
                                                        instance=self.get_information())
            education_form = context['education_form']

            print(education_form.errors)
            if education_form.is_valid():
                if 'education_id' in self.kwargs:
                    try:
                        updated = emp_models.Education.objects.get(id=self.kwargs['education_id'],
                                                                   employee_id=self.kwargs['pk'])
                        updated.degree = education_form.cleaned_data['degree']
                        updated.university = education_form.cleaned_data['university']
                        updated.subject = education_form.cleaned_data['subject']
                        updated.year_of_completion = education_form.cleaned_data['year_of_completion']
                        updated.result_type = education_form.cleaned_data['result_type']
                        updated.result_of_gpa = education_form.cleaned_data['result_of_gpa']
                        updated.out_of = education_form.cleaned_data['out_of']
                        updated.result_of_division = education_form.cleaned_data['result_of_division']
                        updated.grade = education_form.cleaned_data['grade']
                        updated.marks = education_form.cleaned_data['marks']
                        updated.certificate = education_form.cleaned_data['certificate']
                        updated.save()
                        messages.success(self.request, "Updated education qualification")
                        return redirect('employees:employee_education_list', self.kwargs['pk'])
                    except IntegrityError:
                        messages.error(self.request, "Duplicate entry of degree for this employee.")

                else:
                    try:
                        data, created = emp_models.Education.objects. \
                            get_or_create(employee_id=self.kwargs['pk'],
                                          degree=education_form.cleaned_data['degree'],
                                          university=education_form.cleaned_data['university'],
                                          subject=education_form.cleaned_data['subject'],
                                          year_of_completion=education_form.cleaned_data['year_of_completion'],
                                          result_type=education_form.cleaned_data['result_type'],
                                          result_of_gpa=education_form.cleaned_data['result_of_gpa'],
                                          out_of=education_form.cleaned_data['out_of'],
                                          result_of_division=education_form.cleaned_data['result_of_division'],
                                          grade=education_form.cleaned_data['grade'],
                                          marks=education_form.cleaned_data['marks'],
                                          defaults={'degree': education_form.cleaned_data['degree'],
                                                    'university': education_form.cleaned_data['university'],
                                                    'subject': education_form.cleaned_data['subject'],
                                                    'year_of_completion': education_form.cleaned_data[
                                                        'year_of_completion'],
                                                    'result_type': education_form.cleaned_data['result_type'],
                                                    'result_of_gpa': education_form.cleaned_data['result_of_gpa'],
                                                    'out_of': education_form.cleaned_data['out_of'],
                                                    'result_of_division': education_form.cleaned_data[
                                                        'result_of_division'],
                                                    'grade': education_form.cleaned_data['grade'],
                                                    'marks': education_form.cleaned_data['marks'],
                                                    'certificate': education_form.cleaned_data['certificate']})
                        if created:
                            messages.success(self.request, "Created education qualification")
                        else:
                            messages.success(self.request, "Already created.")
                    except IntegrityError:
                        messages.error(self.request, "Duplicate entry of degree for this employee.")

                return redirect('employees:employee_education_create', self.kwargs['pk'])

        return render(request, self.template_name, context)


class EducationDeleteView(LoginRequiredMixin, PermissionMixin, DeleteView):
    """
        Delete a selected education qualification
        Access: Super-Admin, Admin
    """
    model = emp_models.Education
    permission_required = 'delete_education'
    success_message = "Deleted"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(EducationDeleteView, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('employees:employee_education_create', args=[self.kwargs['employee_pk']])

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from payroll.models import PayGrade
from helpers.mixins import PermissionMixin
from helpers.functions import get_organizational_structure


class GradeListView(LoginRequiredMixin, PermissionMixin, ListView):
    """
        show all grade list
        Access: Super-Admin, Admin
        Url: /admin/payroll/master/paygrade/
    """
    template_name = 'payroll/master/paygrade/list.html'
    model = PayGrade
    context_object_name = 'grades'
    permission_required = 'view_grade'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        return context


class GradeCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Add new grade
        Access: Super-Admin, Admin
        Url: /admin/payroll/master/paygrade/create/
    """
    template_name = 'payroll/master/paygrade/create.html'
    model = PayGrade
    fields = ('name', 'status', 'description')
    permission_required = 'add_grade'

    def get(self, request, *args, **kwargs):
        permissions = self.get_current_user_permission_list()
        if request.user.is_authenticated and request.user.is_superuser:
            form = self.form_class(None)
            return render(request, self.template_name, {'form': form, 'permissions': permissions})
        return redirect('/')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            form = self.form_class(request.POST)
            if form.is_valid():
                my_form = form.save(commit=False)
                my_form.created_by = self.request.user
                my_form.save()
                return redirect(reverse_lazy('beehive_admin:hr_policies:grade_list'))

            return render(request, self.template_name, {'form': form})

        return redirect('/')


class GradeUpdateView(LoginRequiredMixin, PermissionMixin, UpdateView):
    """
        Update a selected grade
        Access: Super-Admin, Admin
        Url: /admin/payroll/master/paygrade/<pk>/update
    """
    model = PayGrade
    fields = ('name', 'status', 'description')
    template_name = 'payroll/master/paygrade/update.html'
    success_url = reverse_lazy('beehive_admin:hr_policies:grade_list')
    permission_required = 'change_grade'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        return context

    def form_valid(self, form):
        my_form = form.save(commit=False)
        grade = self.get_object()

        if my_form.name is None:
            my_form.name = grade.name

        my_form.updated_by = self.request.user
        my_form.save()

        return super().form_valid(form)


class GradeDeleteView(LoginRequiredMixin, PermissionMixin, DeleteView):
    """
        Delete a selected grade
        Access: Super-Admin, Admin
        Url: /admin/payroll/master/paygrade/<pk>/delete
    """
    model = PayGrade
    template_name = 'payroll/master/paygrade/delete.html'
    success_url = reverse_lazy('beehive_admin:hr_policies:grade_list')
    context_object_name = 'grade'
    permission_required = 'delete_grade'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        return context

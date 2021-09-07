from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, DeleteView, FormView
from payroll.forms import SalaryGroupCreateForm
from payroll.models import SalaryGroup, SalaryGroupComponent, Component
from helpers.mixins import PermissionMixin
from django.contrib import messages
from helpers.functions import get_organizational_structure


class SalaryGroupList(LoginRequiredMixin, PermissionMixin, ListView):
    """
        List of Salary Group
    """

    model = SalaryGroup
    context_object_name = 'groups'
    template_name = "payroll/salary_group/list.html"
    permission_required = ['add_salarygroup', 'change_salarygroup', 'view_salarygroup', 'delete_salarygroup']

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        paginator = Paginator(self.object_list, 50)
        page = self.request.GET.get('page')
        context['groups'] = paginator.get_page(page)
        index = context['groups'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class SalaryGroupCreate(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Create new Salary Group
    """

    template_name = 'payroll/salary_group/create.html'
    permission_required = 'add_salarygroup'

    def get(self, request, *args, **kwargs):
        context = {
            'form': SalaryGroupCreateForm(),
            'permissions': self.get_current_user_permission_list(),
            'org_items_list': get_organizational_structure()
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = SalaryGroupCreateForm(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {
                'permissions': self.get_current_user_permission_list(),
                'org_items_list': get_organizational_structure(),
                'form': form
            })

        group = form.save(commit=False)
        group.save()

        for i, component in enumerate(request.POST.getlist('component')):
            component_obj = Component.objects.get(id=component)
            SalaryGroupComponent.objects.create(
                salary_group=group,
                component=component_obj
            )

        messages.success(request, f'{group} was created successfully')
        return redirect(reverse_lazy('beehive_admin:payroll:salary_group_list'))


class SalaryGroupUpdate(LoginRequiredMixin, PermissionMixin, FormView):
    """
        Change Salary Group
    """

    form_class = SalaryGroupCreateForm
    template_name = "payroll/salary_group/update.html"
    permission_required = 'change_salarygroup'

    def get_object(self, queryset=None):
        group = SalaryGroup.objects.get(id=self.kwargs.get('pk', ''))
        return get_object_or_404(SalaryGroup, pk=group.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = SalaryGroup.objects.get(id=self.kwargs.get('pk', ''))
        initial = {
            'name': group.name,
            'short_code': group.short_code,
            'description': group.description,
            'status': group.status,
        }
        context['form'] = self.form_class(initial=initial)
        context['group'] = SalaryGroup.objects.get(id=self.kwargs.get('pk', ''))
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['selected'] = SalaryGroupComponent.objects.filter(salary_group=self.get_object())
        return context

    def post(self, request, *args, **kwargs):
        form = SalaryGroupCreateForm(request.POST)

        if not form.my_is_valid():
            return render(request, self.template_name, {
                'permissions': self.get_current_user_permission_list(),
                'org_items_list': get_organizational_structure(),
                'form': form,
                'selected': SalaryGroupComponent.objects.filter(salary_group=self.get_object()),
                'group': SalaryGroup.objects.get(id=self.kwargs.get('pk', ''))
            })

        group = SalaryGroup.objects.get(id=self.get_object().id)

        group.name = form.cleaned_data['name']
        group.short_code = form.cleaned_data['short_code']
        group.description = form.cleaned_data['description']
        group.status = form.cleaned_data['status']
        group.save()

        for i, component in enumerate(request.POST.getlist('component')):
            component_obj = Component.objects.get(id=component)
            SalaryGroupComponent.objects.update_or_create(
                salary_group=group,
                component=component_obj
            )

        selected_list = request.POST.getlist('component')
        group_members = SalaryGroupComponent.objects.filter(salary_group=group)
        if group_members.exists():
            for member in group_members:
                selected = False
                for sel in selected_list:
                    if int(sel) == member.component.id:
                        selected = True
                if not selected:
                    member.delete()

        messages.success(request, f'{group} was updated successfully')
        return redirect(reverse_lazy('beehive_admin:payroll:salary_group_list'))


class SalaryGroupDelete(LoginRequiredMixin, PermissionMixin, DeleteView):
    """
        Delete salary group
    """

    model = SalaryGroup
    success_message = "%(name)s deleted."
    success_url = reverse_lazy("beehive_admin:payroll:salary_group_list")
    permission_required = 'delete_salarygroup'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(SalaryGroupDelete, self).delete(request, *args, **kwargs)

from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, DeleteView, FormView
from payroll.forms import BonusGroupCreateForm
from payroll.models import BonusGroup, BonusGroupComponentMembers, BonusComponent
from helpers.mixins import PermissionMixin
from django.contrib import messages
from helpers.functions import get_organizational_structure


class BonusGroupList(LoginRequiredMixin, PermissionMixin, ListView):
    """
        List of Bonus Group
    """

    model = BonusGroup
    context_object_name = 'groups'
    template_name = "payroll/master/bonus_group/list.html"
    permission_required = ['add_bonusgroup', 'change_bonusgroup', 'view_bonusgroup',
                           'delete_bonusgroup']

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


class BonusGroupCreate(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Create new Bonus Group
    """

    template_name = 'payroll/master/bonus_group/create.html'
    permission_required = 'add_bonusgroup'

    def get(self, request, *args, **kwargs):
        context = {
            'form': BonusGroupCreateForm(),
            'permissions': self.get_current_user_permission_list(),
            'org_items_list': get_organizational_structure()
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = BonusGroupCreateForm(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {
                'permissions': self.get_current_user_permission_list(),
                'org_items_list': get_organizational_structure(),
                'form': form
            })

        group = form.save(commit=False)
        group.save()

        for i, yearly_component in enumerate(request.POST.getlist('yearly_component')):
            component = BonusComponent.objects.get(id=yearly_component)
            BonusGroupComponentMembers.objects.update_or_create(
                group=group,
                component=component
            )

        for i, half_yearly_component in enumerate(request.POST.getlist('half_yearly_component')):
            component = BonusComponent.objects.get(id=half_yearly_component)
            BonusGroupComponentMembers.objects.update_or_create(
                group=group,
                component=component
            )

        for i, quarterly_component in enumerate(request.POST.getlist('quarterly_component')):
            component = BonusComponent.objects.get(id=quarterly_component)
            BonusGroupComponentMembers.objects.update_or_create(
                group=group,
                component=component
            )

        for i, monthly_component in enumerate(request.POST.getlist('monthly_component')):
            component = BonusComponent.objects.get(id=monthly_component)
            BonusGroupComponentMembers.objects.update_or_create(
                group=group,
                component=component
            )

        messages.success(request, f'{group} was created successfully')
        return redirect(reverse_lazy('beehive_admin:payroll:bonus_group_list'))


class BonusGroupUpdate(LoginRequiredMixin, PermissionMixin, FormView):
    """
        Change Bonus Group
    """

    form_class = BonusGroupCreateForm
    template_name = "payroll/master/bonus_group/update.html"
    permission_required = 'change_bonusgroup'

    def get_object(self, queryset=None):
        group = BonusGroup.objects.get(id=self.kwargs.get('pk', ''))
        return get_object_or_404(BonusGroup, pk=group.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = BonusGroup.objects.get(id=self.kwargs.get('pk', ''))
        initial = {
            'name': group.name,
            'short_code': group.short_code,
            'description': group.description,
            'status': group.status,
        }
        context['form'] = self.form_class(initial=initial)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['selected_yearly'] = \
            BonusGroupComponentMembers.objects.filter(group=self.get_object(), component__bonus_period='year')
        context['selected_half_yearly'] = \
            BonusGroupComponentMembers.objects.filter(group=self.get_object(), component__bonus_period='half-year')
        context['selected_quarterly'] = \
            BonusGroupComponentMembers.objects.filter(group=self.get_object(), component__bonus_period='quarter')
        context['selected_monthly'] = \
            BonusGroupComponentMembers.objects.filter(group=self.get_object(), component__bonus_period='month')

        return context

    def post(self, request, *args, **kwargs):
        form = BonusGroupCreateForm(request.POST)

        if not form.my_is_valid():
            return render(request, self.template_name, {
                'permissions': self.get_current_user_permission_list(),
                'org_items_list': get_organizational_structure(),
                'form': form,
                'selected_yearly': BonusGroupComponentMembers.objects.filter(group=self.get_object(),
                                                                             component__bonus_period='year'),
                'selected_half_yearly': BonusGroupComponentMembers.objects.filter(group=self.get_object(),
                                                                                  component__bonus_period='half-year'),
                'selected_quarterly': BonusGroupComponentMembers.objects.filter(group=self.get_object(),
                                                                                component__bonus_period='quarter'),
                'selected_monthly': BonusGroupComponentMembers.objects.filter(group=self.get_object(),
                                                                              component__bonus_period='month')
            })

        group = BonusGroup.objects.get(id=self.get_object().id)

        group.name = form.cleaned_data['name']
        group.short_code = form.cleaned_data['short_code']
        group.description = form.cleaned_data['description']
        group.status = form.cleaned_data['status']
        group.save()

        for i, yearly_component in enumerate(request.POST.getlist('yearly_component')):
            component = BonusComponent.objects.get(id=yearly_component)
            BonusGroupComponentMembers.objects.update_or_create(
                group=group,
                component=component
            )

        for i, half_yearly_component in enumerate(request.POST.getlist('half_yearly_component')):
            component = BonusComponent.objects.get(id=half_yearly_component)
            BonusGroupComponentMembers.objects.update_or_create(
                group=group,
                component=component
            )

        for i, quarterly_component in enumerate(request.POST.getlist('quarterly_component')):
            component = BonusComponent.objects.get(id=quarterly_component)
            BonusGroupComponentMembers.objects.update_or_create(
                group=group,
                component=component
            )

        for i, monthly_component in enumerate(request.POST.getlist('monthly_component')):
            component = BonusComponent.objects.get(id=monthly_component)
            BonusGroupComponentMembers.objects.update_or_create(
                group=group,
                component=component
            )

        selected_yearly_list = request.POST.getlist('yearly_component')
        group_members = \
            BonusGroupComponentMembers.objects.filter(group=group, component__bonus_period='year')
        if group_members.exists():
            for member in group_members:
                selected = False
                for sel in selected_yearly_list:
                    if int(sel) == member.component.id:
                        selected = True
                if not selected:
                    member.delete()

        selected_half_yearly_list = request.POST.getlist('half_yearly_component')
        group_members = \
            BonusGroupComponentMembers.objects.filter(group=group, component__bonus_period='half-year')
        if group_members.exists():
            for member in group_members:
                selected = False
                for sel in selected_half_yearly_list:
                    if int(sel) == member.component.id:
                        selected = True
                if not selected:
                    member.delete()

        selected_quarterly_list = request.POST.getlist('quarterly_component')
        group_members = \
            BonusGroupComponentMembers.objects.filter(group=group, component__bonus_period='quarter')
        if group_members.exists():
            for member in group_members:
                selected = False
                for sel in selected_quarterly_list:
                    if int(sel) == member.component.id:
                        selected = True
                if not selected:
                    member.delete()

        selected_monthly_list = request.POST.getlist('monthly_component')
        group_members = \
            BonusGroupComponentMembers.objects.filter(group=group, component__bonus_period='month')
        if group_members.exists():
            for member in group_members:
                selected = False
                for sel in selected_monthly_list:
                    if int(sel) == member.component.id:
                        selected = True
                if not selected:
                    member.delete()

        messages.success(request, f'{group} was updated successfully')
        return redirect(reverse_lazy('beehive_admin:payroll:bonus_group_list'))


class BonusGroupDelete(LoginRequiredMixin, PermissionMixin, DeleteView):
    """
        Delete Bonus group
    """

    model = BonusGroup
    success_message = "%(name)s deleted."
    context_object_name = 'bonus_group'
    success_url = reverse_lazy("beehive_admin:payroll:bonus_group_list")
    permission_required = 'delete_bonusgroup'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(BonusGroupDelete, self).delete(request, *args, **kwargs)

from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, DeleteView, FormView
from attendance.forms import HolidayGroupCreateForm
from attendance.models import HolidayGroup, HolidayGroupMasterMembers, HolidayMaster
from helpers.mixins import PermissionMixin
from django.contrib import messages
import calendar
from helpers.functions import get_organizational_structure


class HolidayGroupList(LoginRequiredMixin, PermissionMixin, ListView):
    """
        List of Holiday Group
    """

    model = HolidayGroup
    template_name = "attendance/master/holiday_group/list.html"
    permission_required = ['add_holidaygroup', 'change_holidaygroup', 'view_holidaygroup', 'delete_holidaygroup']

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


class HolidayGroupCreate(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Create new Holiday Group
    """

    template_name = 'attendance/master/holiday_group/create.html'
    permission_required = 'add_holidaygroup'

    def get_yearly_list(self, holidays_list):
        my_list = []
        i = 0
        while i < len(holidays_list):
            selected_year = holidays_list[i].start_date.year
            j = i
            holidays = []
            holidays_copy = []
            while j < len(holidays_list):
                if selected_year == holidays_list[j].start_date.year:
                    holidays.append(holidays_list[j])
                    holidays_copy.append(holidays_list[j])
                else:
                    my_list.append((selected_year, tuple(holidays)))
                    holidays_copy.clear()
                    i = j - 1
                    break
                j += 1
            if len(holidays_copy) > 0:
                my_list.append((selected_year, tuple(holidays)))
                holidays_copy.clear()
                i = j - 1
            i += 1
        return tuple(my_list)

    def get_final_lists(self, my_list):
        final_list = []
        years = []
        for year, yearly_holidays in my_list:
            i = 0
            month_list = []
            while i < len(yearly_holidays):
                selected_month = yearly_holidays[i].start_date.month
                j = i
                holidays = []
                holidays_copy = []
                while j < len(yearly_holidays):
                    if selected_month == yearly_holidays[j].start_date.month:
                        holidays.append(yearly_holidays[j])
                        holidays_copy.append(yearly_holidays[j])
                    else:
                        month_list.append((calendar.month_name[selected_month], tuple(holidays)))
                        holidays_copy.clear()
                        i = j - 1
                        break
                    j += 1
                if len(holidays_copy) > 0:
                    month_list.append((calendar.month_name[selected_month], tuple(holidays)))
                    holidays_copy.clear()
                    i = j - 1
                i += 1
            years.append(year)
            final_list.append((year, tuple(month_list)))
        return years, tuple(final_list)

    def get(self, request, *args, **kwargs):
        holidays_qs = HolidayMaster.objects.order_by('start_date__year', 'start_date__month')
        holidays_list = list(holidays_qs)
        yearly_list = self.get_yearly_list(holidays_list)
        years, final_holidays_list = self.get_final_lists(yearly_list)

        context = {
            'form': HolidayGroupCreateForm(),
            'permissions': self.get_current_user_permission_list(),
            'org_items_list': get_organizational_structure(),
            'years': years,
            'final_holidays_list': final_holidays_list
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = HolidayGroupCreateForm(request.POST)

        if not form.is_valid():
            holidays_qs = HolidayMaster.objects.order_by('start_date__year', 'start_date__month')
            holidays_list = list(holidays_qs)
            yearly_list = self.get_yearly_list(holidays_list)
            years, final_holidays_list = self.get_final_lists(yearly_list)

            return render(request, self.template_name, {
                'permissions': self.get_current_user_permission_list(),
                'org_items_list': get_organizational_structure(),
                'form': form,
                'years': years,
                'final_holidays_list': final_holidays_list
            })

        group = form.save(commit=False)
        group.save()

        for i, holiday in enumerate(request.POST.getlist('holiday')):
            master = HolidayMaster.objects.get(id=holiday)
            HolidayGroupMasterMembers.objects.create(
                group=group,
                master=master
            )

        messages.success(request, f'{group} was created successfully')
        return redirect(reverse_lazy('beehive_admin:attendance:holiday_group_list'))


class HolidayGroupUpdate(LoginRequiredMixin, PermissionMixin, FormView):
    """
        Change Holiday Group
    """

    form_class = HolidayGroupCreateForm
    template_name = "attendance/master/holiday_group/update.html"
    permission_required = 'change_holidaygroup'

    def get_object(self, queryset=None):
        group = HolidayGroup.objects.get(id=self.kwargs.get('pk', ''))
        return get_object_or_404(HolidayGroup, pk=group.id)

    def get_yearly_list(self, holidays_list):
        my_list = []
        i = 0
        while i < len(holidays_list):
            selected_year = holidays_list[i].start_date.year
            j = i
            holidays = []
            holidays_copy = []
            while j < len(holidays_list):
                if selected_year == holidays_list[j].start_date.year:
                    holidays.append(holidays_list[j])
                    holidays_copy.append(holidays_list[j])
                else:
                    my_list.append((selected_year, tuple(holidays)))
                    holidays_copy.clear()
                    i = j - 1
                    break
                j += 1
            if len(holidays_copy) > 0:
                my_list.append((selected_year, tuple(holidays)))
                holidays_copy.clear()
                i = j - 1
            i += 1
        return tuple(my_list)

    def get_final_lists(self, my_list):
        final_list = []
        years = []
        for year, yearly_holidays in my_list:
            i = 0
            month_list = []
            while i < len(yearly_holidays):
                selected_month = yearly_holidays[i].start_date.month
                j = i
                holidays = []
                holidays_copy = []
                while j < len(yearly_holidays):
                    if selected_month == yearly_holidays[j].start_date.month:
                        holidays.append(yearly_holidays[j])
                        holidays_copy.append(yearly_holidays[j])
                    else:
                        month_list.append((calendar.month_name[selected_month], tuple(holidays)))
                        holidays_copy.clear()
                        i = j - 1
                        break
                    j += 1
                if len(holidays_copy) > 0:
                    month_list.append((calendar.month_name[selected_month], tuple(holidays)))
                    holidays_copy.clear()
                    i = j - 1
                i += 1
            years.append(year)
            final_list.append((year, tuple(month_list)))
        return years, tuple(final_list)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = HolidayGroup.objects.get(id=self.kwargs.get('pk', ''))
        initial = {
            'name': group.name,
            'short_code': group.short_code,
            'description': group.description,
            'status': group.status,
        }
        context['form'] = self.form_class(initial=initial)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['selected'] = HolidayGroupMasterMembers.objects.filter(group=self.get_object())
        holidays_qs = HolidayMaster.objects.order_by('start_date__year', 'start_date__month')
        holidays_list = list(holidays_qs)
        yearly_list = self.get_yearly_list(holidays_list)
        years, final_holidays_list = self.get_final_lists(yearly_list)
        context['years'] = years
        context['final_holidays_list'] = final_holidays_list
        return context

    def post(self, request, *args, **kwargs):
        form = HolidayGroupCreateForm(request.POST)

        if not form.my_is_valid():
            holidays_qs = HolidayMaster.objects.order_by('start_date__year', 'start_date__month')
            holidays_list = list(holidays_qs)
            yearly_list = self.get_yearly_list(holidays_list)
            years, final_holidays_list = self.get_final_lists(yearly_list)

            return render(request, self.template_name, {
                'permissions': self.get_current_user_permission_list(),
                'org_items_list': get_organizational_structure(),
                'form': form,
                'selected': HolidayGroupMasterMembers.objects.filter(group=self.get_object()),
                'years': years,
                'final_holidays_list': final_holidays_list
            })

        group = HolidayGroup.objects.get(id=self.get_object().id)

        group.name = form.cleaned_data['name']
        group.short_code = form.cleaned_data['short_code']
        group.description = form.cleaned_data['description']
        group.status = form.cleaned_data['status']
        group.save()

        for i, holiday in enumerate(request.POST.getlist('holiday')):
            master = HolidayMaster.objects.get(id=holiday)
            HolidayGroupMasterMembers.objects.update_or_create(
                group=group,
                master=master
            )

        selected_list = request.POST.getlist('holiday')
        group_members = HolidayGroupMasterMembers.objects.filter(group=group)
        if group_members.exists():
            for member in group_members:
                selected = False
                for sel in selected_list:
                    if int(sel) == member.master.id:
                        selected = True
                if not selected:
                    member.delete()

        messages.success(request, f'{group} was updated successfully')
        return redirect(reverse_lazy('beehive_admin:attendance:holiday_group_list'))


class HolidayGroupDelete(LoginRequiredMixin, PermissionMixin, DeleteView):
    """
            Delete holiday group
        """

    model = HolidayGroup
    template_name = "attendance/master/holiday_group/delete.html"
    success_message = "%(name)s deleted."
    success_url = reverse_lazy("beehive_admin:attendance:holiday_group_list")
    permission_required = 'delete_holidaygroup'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(HolidayGroupDelete, self).delete(request, *args, **kwargs)

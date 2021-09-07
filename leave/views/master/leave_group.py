from django.core.paginator import Paginator
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView, DeleteView, ListView
from employees.models import LeaveManage, JobInformation
from leave.forms import *
from helpers.mixins import PermissionMixin
from django.conf import settings
from django.contrib import messages
from leave.views.process import get_frequency_convert_time_unit, get_half_year, \
    get_quarter, convert_time_unit_into_seconds
import math
from datetime import datetime, timedelta
from django.db.models import Q
from helpers.functions import get_organizational_structure


class LeaveGroupListView(LoginRequiredMixin, PermissionMixin, ListView):
    permission_required = ['view_leavegroup']
    template_name = 'leave/master/leave_group/list.html'
    model = LeaveGroup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        paginator = Paginator(self.object_list, 50)
        page = self.request.GET.get('page')
        context['leave_group_list'] = paginator.get_page(page)
        index = context['leave_group_list'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class LeaveGroupCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    """Show the form to create a leave group."""

    template_name = 'leave/master/leave_group/create.html'
    model = LeaveGroup
    form_class = LeaveGroupForm
    permission_required = ['add_leavegroup']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        if 'form' not in context:
            context['form'] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.save()
            new_form.leave.set(request.POST.getlist('leave'))
            return HttpResponseRedirect(reverse('beehive_admin:leave:leave_group_edit', kwargs={'pk': new_form.id}))
        return render(request, self.template_name, {'form': form,
                                                    'permissions': self.get_current_user_permission_list(),
                                                    'org_items_list': get_organizational_structure()})


class LeaveGroupUpdateView(LoginRequiredMixin, PermissionMixin, TemplateView):
    """
        Change LeaveGroup
    """
    login_url = settings.LOGIN_URL
    form_class = LeaveGroupForm
    settings_form_class = LeaveSettingsForm
    success_message = "Updated Successfully"
    template_name = "leave/master/leave_group/update.html"
    success_url = reverse_lazy("beehive_admin:leave:leave_group_list")
    permission_required = 'change_leavegroup'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        leave_form, restriction_form = self.get_leave_form()
        if 'form' not in context:
            context['form'] = self.form_class(instance=self.get_leave_group_instance())
        if 'settings_form' not in context:
            context['settings_form'] = leave_form
        if 'restriction_form' not in context:
            context['restriction_form'] = restriction_form
        return context

    def get_leave_group_instance(self):
        return LeaveGroup.objects.get(id=self.kwargs['pk'])

    def get_leave_instance(self, leave):
        instance = LeaveGroupSettings.objects.filter(leave_group=self.kwargs['pk'], leave_name=leave).first()
        return instance

    def get_leave_form(self):
        data = self.get_leave_group_instance()
        leave_form = list()
        restriction_form = list()
        for leave in data.leave.all():
            leave_group_settings = self.get_leave_instance(leave.id)
            leave_form.append(self.settings_form_class(instance=leave_group_settings, prefix=str(leave.id)))
            restriction_form.append(RestrictionFormset(instance=leave_group_settings, prefix=str(leave.id)))
        return leave_form, restriction_form

    def post(self, request, *args, **kwargs):
        context = dict()
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']
        leave_form, restriction_form = self.get_leave_form()
        leave_group_ins = self.get_leave_group_instance()

        if 'form' not in context:
            context['form'] = self.form_class(instance=leave_group_ins)
        if 'settings_form' not in context:
            context['settings_form'] = leave_form
        if 'restriction_form' not in context:
            context['restriction_form'] = restriction_form

        """
            leave group update form
        """
        if 'form1' in request.POST:
            form = self.form_class(request.POST, instance=leave_group_ins)
            context['form'] = form
            if form.is_valid():
                # check this leave group which employee are assigned
                leave_manage_qs = LeaveManage.objects.filter(leave_group_id=self.kwargs['pk']).values('employee')

                # if leave checkbox change also remove the leave group settings model row
                if leave_group_ins:
                    for leave_id in leave_group_ins.leave.all():
                        if str(leave_id.id) not in request.POST.getlist('leave'):
                            LeaveGroupSettings.objects.filter(leave_name=leave_id.id,
                                                              leave_group=self.kwargs['pk']).delete()
                            # delete leave remaining if any leave deleted
                            if leave_manage_qs:
                                for em in leave_manage_qs:
                                    LeaveRemaining.objects.filter(status=True, leave=leave_id,
                                                                  employee_id=em['employee']).delete()
                        # # add leave remaining if any leave insert
                        if leave_manage_qs:
                            for em in leave_manage_qs:
                                if form.cleaned_data['status'] is True:
                                    total_remain, total_avail_leave = set_leave_remaining(em['employee'],
                                                                                          leave_id, self.kwargs['pk'])
                                    in_seconds = convert_time_unit_into_seconds(leave_id, total_remain)
                                    total_avail_leave_in_seconds = convert_time_unit_into_seconds(leave_id,
                                                                                                  total_avail_leave)
                                    LeaveRemaining.objects. \
                                        update_or_create(status=True, leave=leave_id, employee_id=em['employee'],
                                                         defaults={'remaining_in_seconds': in_seconds,
                                                                   'availing_in_seconds': total_avail_leave_in_seconds}
                                                         )
                                else:
                                    # if status false delete all remaining
                                    LeaveRemaining.objects.filter(status=True, leave=leave_id,
                                                                  employee_id=em['employee']).delete()

                form = form.save(commit=False)
                form.save()
                form.leave.set(request.POST.getlist('leave'))
                messages.success(self.request, self.success_message)
                return HttpResponseRedirect(reverse('beehive_admin:leave:leave_group_edit', kwargs={'pk': form.id}))

        """
            leave setting 
        """
        form_name = request.POST.get('form_name')
        if form_name in request.POST:
            leave_form = list()
            restriction_form = list()
            for leave in leave_group_ins.leave.all():
                leave_group_settings = self.get_leave_instance(leave.id)
                if str(leave.id) == form_name:
                    settings = self.settings_form_class(request.POST, instance=leave_group_settings,
                                                        prefix=str(leave.id))
                    restriction = RestrictionFormset(request.POST, instance=leave_group_settings, prefix=str(leave.id))
                    context['active_tab'] = 'menu_' + str(form_name)
                    if settings.is_valid() and restriction.is_valid():
                        settings_form = settings.save(commit=False)
                        settings_form.leave_group_id = self.kwargs['pk']
                        settings_form.leave_name_id = leave.id
                        settings_form.save()

                        # check this leave group which employee are assigned
                        leave_manage_qs = LeaveManage.objects.filter(leave_group_id=self.kwargs['pk']).values(
                            'employee')
                        # add leave remaining if any leave insert
                        if leave_manage_qs:
                            for em in leave_manage_qs:
                                total_remain, total_avail_leave = set_leave_remaining(em['employee'], leave,
                                                                                      self.kwargs['pk'])
                                in_seconds = convert_time_unit_into_seconds(leave, total_remain)
                                total_avail_leave_in_seconds = convert_time_unit_into_seconds(leave, total_avail_leave)
                                LeaveRemaining.objects. \
                                    update_or_create(status=True, leave=leave, employee_id=em['employee'],
                                                     defaults={'remaining_in_seconds': in_seconds,
                                                               'availing_in_seconds': total_avail_leave_in_seconds}
                                                     )
                        # Save Restriction for leave
                        for restrict in restriction:
                            if restrict.is_valid():
                                if restrict.cleaned_data.get('can_enjoy') is not None and \
                                        restrict.cleaned_data.get('within') is not None:
                                    restrict = restrict.save(commit=False)
                                    restrict.leave_settings = settings_form
                                    restrict.save()
                                forms = restriction.save(commit=False)
                                for obj in restriction.deleted_objects:
                                    obj.delete()
                            else:
                                leave_form.append(settings)
                                restriction_form.append(restriction)
                                context['settings_form'] = leave_form
                                context['restriction_form'] = restriction_form
                                return render(request, self.template_name, context)
                        messages.success(self.request, "Leave settings successfully saved.")
                        # return redirect('beehive_admin:leave:leave_group_edit', pk=self.kwargs['pk'])
                        #                         # return HttpResponseRedirect(
                        #     reverse('beehive_admin:leave:leave_group_edit',
                        #             kwargs={'pk': self.kwargs['pk'], 'active_tab': 'menu_' + str(form_name)}))

                    leave_form.append(settings)
                    restriction_form.append(restriction)
                else:
                    leave_form.append(self.settings_form_class(instance=leave_group_settings, prefix=str(leave.id)))
                    restriction_form.append(RestrictionFormset(instance=leave_group_settings, prefix=str(leave.id)))
            context['settings_form'] = leave_form
            context['restriction_form'] = restriction_form

        return render(request, self.template_name, context)


class LeaveGroupDeleteView(LoginRequiredMixin, PermissionMixin, DeleteView):
    """
        Delete leave_group
    """
    model = LeaveGroup
    success_message = "%(name)s deleted."
    permission_required = 'delete_leavegroup'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()

        # check this leave group which employee are assigned
        leave_manage_qs = LeaveManage.objects.filter(leave_group=obj).values(
            'employee')
        # delete leave remaining
        if leave_manage_qs:
            for leave_id in obj.leave.all():
                for em in leave_manage_qs:
                    LeaveRemaining.objects.filter(status=True, leave=leave_id,
                                                  employee_id=em['employee']).delete()

        messages.success(self.request, self.success_message % obj.__dict__)
        return super(LeaveGroupDeleteView, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('beehive_admin:leave:leave_group_list')


def set_leave_remaining(emp, leave, leave_group):
    credit = 0
    total_remain = 0
    total_avail_leave = 0
    try:
        leave_settings = LeaveGroupSettings.objects.filter(leave_name=leave, leave_group_id=leave_group)
        job = JobInformation.objects.filter(employee_id=emp).last()
        if leave.leave_credit_type == 'fixed':
            if leave_settings:
                credit = leave_settings[0].leave_credit
            if leave.variable_with_time is True:
                have_credit = get_frequency_convert_time_unit(leave.available_frequency_unit,
                                                              leave.available_frequency_number,
                                                              leave.time_unit_basis, job.date_of_joining,
                                                              credit)
                if leave.round_of_time == 'floor':
                    credit = math.floor(have_credit)
                if leave.round_of_time == 'ceiling':
                    credit = math.ceil(have_credit)
                if leave.round_of_time == 'nearest':
                    credit = round(have_credit)

        sum_credit = LeaveAvail.objects.filter(employee=emp, avail_leave=leave, status=1)
        today = datetime.now()
        avail_this_period = 0

        if leave.available_frequency_unit == 'day':
            sum_credit = sum_credit.filter(
                Q(start_date=today) | Q(end_date=today))
            for avail in sum_credit:
                delta = avail.end_date - avail.start_date
                divide_day = delta.days
                divide_credit = avail.credit_seconds / (divide_day + 1)
                for i in range(delta.days + 1):
                    day = avail.start_date + timedelta(days=i)
                    avail_this_period += divide_credit
        elif leave.available_frequency_unit == 'week':
            start_week = today - timedelta(today.weekday())
            end_week = start_week + timedelta(weeks=int(leave.available_frequency_number))
            sum_credit = sum_credit.filter(Q(start_date__range=[start_week.date(), end_week.date()]) | Q(
                end_date__range=[start_week.date(), end_week.date()]))
            for avail in sum_credit:
                delta = avail.end_date - avail.start_date
                divide_day = delta.days

                divide_credit = avail.credit_seconds / (divide_day + 1)
                for i in range(delta.days + 1):
                    day = avail.start_date + timedelta(days=i)
                    # check the date exists in range of week
                    week_delta = end_week.date() - start_week.date()
                    for w in range(week_delta.days + 1):
                        if day == start_week.date() + timedelta(days=w):
                            avail_this_period += divide_credit
        elif leave.available_frequency_unit == 'month':
            sum_credit = sum_credit.filter(
                Q(start_date__month=today.month, start_date__year=today.year) | Q(end_date__month=today.month,
                                                                                  end_date__year=today.year))
            for avail in sum_credit:
                delta = avail.end_date - avail.start_date
                divide_day = delta.days
                divide_credit = avail.credit_seconds / (divide_day + 1)
                for i in range(delta.days + 1):
                    day = avail.start_date + timedelta(days=i)
                    avail_this_period += divide_credit
        elif leave.available_frequency_unit == 'year':
            divide_year = (today.year - job.date_of_joining.year) % int(leave.available_frequency_number)
            start_year = today.year - divide_year
            end_year = today.year
            sum_credit = sum_credit.filter(
                Q(start_date__year__gte=start_year) | Q(end_date__year__lte=end_year))
            for avail in sum_credit:
                delta = avail.end_date - avail.start_date
                if avail.end_date == avail.start_date:
                    avail_this_period += avail.credit_seconds
                else:
                    divide_day = delta.days
                    if divide_day > 0:
                        divide_credit = avail.credit_seconds / (divide_day + 1)
                        for i in range(delta.days + 1):
                            day = avail.start_date + timedelta(days=i)
                            # check the date exists in range of year
                            if day.year in range(start_year, end_year + 1):
                                avail_this_period += divide_credit

        elif leave.available_frequency_unit == 'quarter':
            start_quarter, end_quarter = get_quarter(today)
            sum_credit = sum_credit.filter(Q(start_date__range=[start_quarter.date(), end_quarter.date()]) | Q(
                end_date__range=[start_quarter.date(), end_quarter.date()]))
            for avail in sum_credit:
                delta = avail.end_date - avail.start_date
                divide_day = delta.days
                divide_credit = avail.credit_seconds / (divide_day + 1)
                for i in range(delta.days + 1):
                    day = avail.start_date + timedelta(days=i)
                    # check the date exists in range of quarter
                    quarter_delta = end_quarter.date() - start_quarter.date()
                    for q in range(quarter_delta.days + 1):
                        if day == start_quarter.date() + timedelta(days=q):
                            avail_this_period += divide_credit
        else:
            start_half, end_half = get_half_year(today)
            sum_credit = sum_credit.filter(Q(start_date__range=[start_half.date(), end_half.date()]) | Q(
                end_date__range=[start_half.date(), end_half.date()]))
            for avail in sum_credit:
                delta = avail.end_date - avail.start_date
                divide_day = delta.days
                avail_credit = avail.credit_seconds
                if divide_day < 0:
                    divide_day = 0
                divide_credit = avail_credit / (divide_day + 1)
                for i in range(delta.days + 1):
                    day = avail.start_date + timedelta(days=i)
                    quarter_delta = end_half.date() - start_half.date()
                    for q in range(quarter_delta.days + 1):
                        if day == start_half.date() + timedelta(days=q):
                            avail_this_period += divide_credit

        if leave.time_unit_basis == 'hour':
            total_avail = avail_this_period / 3600
        elif leave.time_unit_basis == 'day':
            total_avail = (avail_this_period / 3600) / 24
        elif leave.time_unit_basis == 'week':
            total_avail = avail_this_period / (3600 * 7 * 24)
        else:
            total_avail = avail_this_period / (3600 * 30 * 24)
        total_remain = credit - total_avail
        total_avail_leave = total_avail
        return total_remain, total_avail_leave
    except Exception as e:
        print(e)
        return total_remain, total_avail_leave

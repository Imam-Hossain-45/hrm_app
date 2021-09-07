from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.validators import EMPTY_VALUES
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, DeleteView
import math
import datetime

from employees.models import LeaveManage, Employment
from helpers.functions import get_organizational_structure
from helpers.mixins import PermissionMixin
from leave.forms import LeaveEntryForm, LeaveApprovalForm
from leave.models import LeaveRemaining, LeaveGroupSettings, LeaveEntry, LeaveMaster, LeaveApprovalComment
from leave.views import (
    get_frequency_convert_time_unit, get_sandwich_leave, get_remaining_leave, get_minimum_gap, get_restriction
)
from user_management.workflow import Approval


def get_query_information(query):
    try:
        emp = LeaveManage.objects.get(employee_id=query)
        job = emp.employee.employee_job_information.latest('updated_at')
        information = {
            'name': emp.employee,
            'designation': job.designation.name if job.designation not in EMPTY_VALUES else '',
            'employee_id': emp.employee.employee_id,
            'company': job.company.name if job.company not in EMPTY_VALUES else '',
            'division': job.division.name if job.division not in EMPTY_VALUES else '',
            'department': job.department.name if job.department not in EMPTY_VALUES else '',
            'business_unit': job.business_unit.name if job.business_unit not in EMPTY_VALUES else '',
            'project': job.project.name if job.project not in EMPTY_VALUES else ''
        }

        leave_list = []
        LEAVE_CHOICES = [('', '----'), ]
        leave_remain_qs = LeaveRemaining.objects.filter(employee_id=query, status=True, leave__status=True)
        for leave_remain in leave_remain_qs:
            credit = 0
            leave = leave_remain.leave
            try:
                leave_settings = LeaveGroupSettings.objects.get(leave_name=leave, leave_group=emp.leave_group)
                if leave.leave_credit_type == 'fixed':
                    credit = leave_settings.leave_credit
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
            except:
                credit = 0
                # raise

            if leave.time_unit_basis == 'hour':
                total_remain = leave_remain.remaining_in_seconds / 3600
                # get total avail leave
                total_avail = int(leave_remain.availing_in_seconds) / 3600
            elif leave.time_unit_basis == 'day':
                total_remain = (leave_remain.remaining_in_seconds / 3600) / 24
                total_avail = int(leave_remain.availing_in_seconds) / 3600 / 24
            elif leave.time_unit_basis == 'week':
                total_remain = leave_remain.remaining_in_seconds / (3600 * 7 * 24)
                total_avail = int(leave_remain.availing_in_seconds) / (3600 * 7 * 24)
            else:
                total_remain = leave_remain.remaining_in_seconds / (3600 * 30 * 24)
                total_avail = int(leave_remain.availing_in_seconds) / (3600 * 30 * 24)

            data = {
                'type': leave,
                'credit': str(credit) + ' ' + leave.time_unit_basis,
                'avail': (str(round(total_avail, 2)) if total_avail > 0 else str(0)) + ' ' + leave.time_unit_basis,
                'remaining': (str(round(total_remain, 2)) if total_remain > 0 else str(
                    0)) + ' ' + leave.time_unit_basis,
            }

            # create leave type choice field
            if data['remaining'] is not 0:
                choices = (leave.id, leave.name)
                LEAVE_CHOICES.append(choices)

            leave_list.append(data)

        return information, leave_list, LEAVE_CHOICES
    except Exception as e:
        return e


class LeaveApplyView(LoginRequiredMixin, UserPassesTestMixin, PermissionMixin, TemplateView):
    template_name = 'self_panel/leave/apply.html'

    def test_func(self):
        return self.request.user.self_panel and self.request.user.employee

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee_id = self.request.user.employee_id
        info_qs = get_query_information(employee_id)
        info, leave_list, choices = info_qs

        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['info'] = info
        context['leave_list'] = leave_list
        context['last_apply_leave_list'] = LeaveEntry.objects.filter(employee_id=employee_id,
                                                                     leave_type__status=True).last()
        context['form'] = LeaveEntryForm(choices)

        return context

    def get_avail_capability(self, query, leave_type):
        employment = Employment.objects.get(employee_id=query)
        leave_group = LeaveManage.objects.get(employee_id=query)
        try:
            leave_settings = LeaveGroupSettings.objects.get(leave_group=leave_group.leave_group,
                                                            leave_name_id=leave_type)

            # Can apply for a leave or not depend on job status
            avail_employee_in = leave_settings.avail_employee_in
            if avail_employee_in is not None:
                if avail_employee_in == 'probation_period':
                    if employment.date_of_actual_confirmation > datetime.datetime.now().date():
                        return True
                    else:
                        return "In probation period cannot apply for this leave."
                if avail_employee_in == 'confirmed_stage':
                    if employment.date_of_actual_confirmation < datetime.datetime.now().date():
                        return True
                    else:
                        return "In confirmation stage cannot apply for this leave."
            else:
                can_enjoy = leave_settings.can_enjoy
                can_enjoy_unit = leave_settings.can_enjoy_unit
                job = leave_group.employee.employee_job_information.latest('updated_at')
                if can_enjoy_unit == 'day':
                    after_joining = job.date_of_joining + datetime.timedelta(days=int(can_enjoy))
                elif can_enjoy_unit == 'week':
                    after_joining = job.date_of_joining + datetime.timedelta(days=int(can_enjoy) * 7)
                elif can_enjoy_unit == 'month':
                    after_joining = job.date_of_joining + datetime.timedelta(days=int(can_enjoy) * 30)
                else:
                    after_joining = datetime.date(year=job.date_of_joining.year + 1, month=job.date_of_joining.month,
                                                  day=job.date_of_joining.day)
                if after_joining < datetime.datetime.now().date():
                    return True
                else:
                    return "Cannot enjoy this leave."
        except:
            return "Not eligible for this leave."
        return "Cannot avail for this leave."

    def get_leave_information(self, leave_type, start_date, end_date, start_time, end_time):
        leave = LeaveMaster.objects.get(id=leave_type)
        if leave.document_required:
            tolerance = leave.tolerance_limit
            tolerance_unit = leave.tolerance_limit_unit
            if start_time is not None and end_time is not None:
                data = datetime.datetime.combine(datetime.datetime.strptime(end_date, "%Y-%m-%d"),
                                                 datetime.datetime.strptime(end_time,
                                                                            "%H:%M").time()) - datetime.datetime.combine(
                    datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                    datetime.datetime.strptime(start_time, "%H:%M").time())
                if tolerance_unit == 'hours':
                    if tolerance * 3600 <= data.total_seconds():
                        return False
                if tolerance_unit == 'days':
                    if tolerance * 24 * 3600 <= data.total_seconds():
                        return False
                if tolerance_unit == 'months':
                    if tolerance * 30 * 24 * 3600 <= data.total_seconds():
                        return False
            else:
                date = datetime.datetime.strptime(end_date, '%Y-%m-%d') - datetime.datetime.strptime(start_date,
                                                                                                     '%Y-%m-%d')
                data = date.days + 1
                if tolerance_unit == 'hours':
                    if tolerance <= data * 24:
                        return False
                if tolerance_unit == 'days':
                    if tolerance <= data:
                        return False
                if tolerance_unit == 'months':
                    if tolerance <= data / 30:
                        return False
        return True

    def get_before_availing_leave(self, leave_type, start_date, start_time):
        leave = LeaveMaster.objects.get(id=leave_type)
        validation_message = ''
        if leave.before_availing_leave:
            before_minimum = leave.before_minimum
            before_minimum_unit = leave.before_minimum_unit
            before_maximum = leave.before_maximum
            before_maximum_unit = leave.before_maximum_unit

            result = True
            if start_time is not None:
                data = datetime.datetime.combine(datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                                                 datetime.datetime.strptime(start_time,
                                                                            "%H:%M").time()) - datetime.datetime.now()
            else:
                data = datetime.datetime.strptime(start_date, '%Y-%m-%d') - datetime.datetime.now()

            data = data.total_seconds()
            if data >= 0:
                if before_minimum_unit == 'hours':
                    if before_minimum * 3600 >= data:
                        result = False
                elif before_minimum_unit == 'days':
                    if before_minimum * 24 * 3600 >= data:
                        result = False
                else:
                    if before_minimum * 30 * 24 * 3600 >= data:
                        result = False

                if before_maximum_unit == 'hours':
                    if before_maximum * 3600 < data:
                        result = False
                elif before_maximum_unit == 'days':
                    if before_maximum * 24 * 3600 < data:
                        result = False
                else:
                    if before_maximum * 30 * 24 * 3600 < data:
                        result = False
            else:
                result = False
            if result is False:
                validation_message = "Application required for this leave minimum " + str(
                    before_minimum) + ' ' + before_minimum_unit + " and maximum " + str(
                    before_maximum) + ' ' + before_maximum_unit + " before."
        return validation_message

    def get_after_availing_leave(self, leave_type, end_date, end_time):
        leave = LeaveMaster.objects.get(id=leave_type)
        validation_message = ''
        if leave.after_availing_leave:
            after_maximum = leave.after_maximum
            after_maximum_unit = leave.after_maximum_unit

            result = True
            if end_time is not None:
                data = datetime.datetime.now() - datetime.datetime.combine(
                    datetime.datetime.strptime(end_date, "%Y-%m-%d"),
                    datetime.datetime.strptime(end_time,
                                               "%H:%M").time())
            else:
                data = datetime.datetime.now() - datetime.datetime.strptime(end_date, '%Y-%m-%d')

            data = data.total_seconds()
            if data >= 0:
                if after_maximum_unit == 'hours':
                    if after_maximum * 3600 < data:
                        result = False
                elif after_maximum_unit == 'days':
                    if after_maximum * 24 * 3600 < data:
                        result = False
                else:
                    if after_maximum * 30 * 24 * 3600 < data:
                        result = False
            else:
                result = False
            if result is False:
                validation_message = "Can apply within " + str(after_maximum) + ' ' + after_maximum_unit
        return validation_message

    def get_limit_at_a_time(self, query, leave_type, start_date, end_date, start_time, end_time, sandwich_leave):
        validation_message = ''
        leave_group = LeaveManage.objects.get(employee_id=query)
        leave_settings = LeaveGroupSettings.objects.get(leave_group=leave_group.leave_group, leave_name_id=leave_type)
        if leave_settings.minimum_enjoy or leave_settings.maximum_enjoy:
            time_unit = leave_settings.leave_name.time_unit_basis
            if start_time is not None and end_time is not None:
                data = datetime.datetime.combine(datetime.datetime.strptime(end_date, "%Y-%m-%d"),
                                                 datetime.datetime.strptime(end_time,
                                                                            "%H:%M").time()) - datetime.datetime.combine(
                    datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                    datetime.datetime.strptime(start_time, "%H:%M").time())
                data_in_seconds = data.total_seconds()
            else:
                s_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
                e_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
                data = e_date - s_date
                if sandwich_leave is False:
                    temp_sandwich = get_sandwich_leave(int(query), s_date, e_date)
                    deduct_sandwich = int(temp_sandwich) * 24 * 3600
                else:
                    deduct_sandwich = 0
                data_in_seconds = (int(data.days + 1) * 24 * 3600) - deduct_sandwich
            data = True
            if time_unit == 'hour':
                if leave_settings.minimum_enjoy:
                    minimum = int(leave_settings.minimum_enjoy) * 3600
                    if minimum > data_in_seconds:
                        data = False
                if leave_settings.maximum_enjoy:
                    maximum = int(leave_settings.maximum_enjoy) * 3600
                    if maximum < data_in_seconds:
                        data = False
            elif time_unit == 'day':
                if leave_settings.minimum_enjoy:
                    minimum = int(leave_settings.minimum_enjoy) * 24 * 3600
                    if minimum > data_in_seconds:
                        data = False
                if leave_settings.maximum_enjoy:
                    maximum = int(leave_settings.maximum_enjoy) * 24 * 3600
                    if maximum < data_in_seconds:
                        data = False
            elif time_unit == 'week':
                if leave_settings.minimum_enjoy:
                    minimum = int(leave_settings.minimum_enjoy) * 7 * 24 * 3600
                    if minimum > data_in_seconds:
                        data = False
                if leave_settings.maximum_enjoy:
                    maximum = int(leave_settings.maximum_enjoy) * 7 * 24 * 3600
                    if maximum < data_in_seconds:
                        data = False
            else:
                if leave_settings.minimum_enjoy:
                    minimum = int(leave_settings.minimum_enjoy) * 30 * 24 * 3600
                    if minimum > data_in_seconds:
                        data = False
                if leave_settings.maximum_enjoy:
                    maximum = int(leave_settings.maximum_enjoy) * 30 * 24 * 3600
                    if maximum < data_in_seconds:
                        data = False
            if data is False:
                validation_message = "Can apply minimum " + str(
                    leave_settings.minimum_enjoy) + " " + time_unit + " and maximum " + str(
                    leave_settings.maximum_enjoy) + " " + time_unit + " at a time."
            else:
                validation_message = ''
        return validation_message

    def post(self, request, *args, **kwargs):
        context = dict()
        query = request.user.employee_id
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        if query is not None:
            info, leave_list, choices = get_query_information(query)
            context['info'] = info
            context['leave_list'] = leave_list
            context['last_apply_leave_list'] = LeaveEntry.objects.filter(employee_id=query,
                                                                         leave_type__status=True).last()
            context['form'] = LeaveEntryForm(choices, request.POST, files=request.FILES)

            def convert_time(t):
                parts = t.split(':')
                if len(parts[0]) == 1:
                    parts[0] = '0{}'.format(parts[0])
                    return ':'.join(parts)
                else:
                    return t

            post_dict = self.request.POST.copy()
            # start and end time validation
            if self.request.POST.get('start_time').strip() not in ['', None]:
                post_dict['start_time'] = datetime.datetime.strptime(convert_time(self.request.POST['start_time']),
                                                                     '%I:%M %p')
                post_dict['start_time'] = post_dict['start_time'].strftime('%H:%M')
            if self.request.POST.get('end_time').strip() not in ['', None]:
                post_dict['end_time'] = datetime.datetime.strptime(convert_time(self.request.POST['end_time']),
                                                                   '%I:%M %p')
                post_dict['end_time'] = post_dict['end_time'].strftime('%H:%M')
            form = LeaveEntryForm(choices, data=post_dict, files=request.FILES)

            # if leave type time unit is hour, start time and end time field will required
            try:
                leave_master = LeaveMaster.objects.get(id=request.POST['leave_type'])
                if leave_master.fractional:
                    form.fields['start_time'].required = True
                    form.fields['end_time'].required = True
            except:
                leave_master = ''
            context['form'] = form
            if form.is_valid():
                # superuser or management has no restriction for apply
                # if there have no credit list of remaining will 0 and
                # availing will be increased by total leave entry

                after_availing_data = True
                avail_capability = self.get_avail_capability(query, request.POST['leave_type'])

                if avail_capability is True:
                    # validation for partial leave and fractional

                    if leave_master.partial_leave_allowed:
                        start_time = post_dict['start_time'] or None
                        end_time = post_dict['end_time'] or None
                    elif leave_master.fractional:
                        start_time = post_dict['start_time'] or None
                        end_time = post_dict['end_time'] or None
                    else:
                        start_time = None
                        end_time = None

                    # validation for remaining leave
                    end_time, availing, remain_leave, total_avail, msg = \
                        get_remaining_leave(query, request.POST['leave_type'], request.POST['start_date'],
                                            request.POST['end_date'], start_time, end_time,
                                            leave_master.sandwich_leave_allowed)

                    if msg is '':
                        remaining_data = True
                    else:
                        remaining_data = False
                        messages.error(self.request, msg)

                    # validation for document required
                    if request.POST.get('attachment') is '':
                        if self.get_leave_information(request.POST['leave_type'], request.POST['start_date'],
                                                      request.POST['end_date'], start_time,
                                                      end_time) is True:
                            attachment_data = True
                        else:
                            attachment_data = False
                            messages.error(self.request, "The document is required.")
                    else:
                        attachment_data = True

                    # validation for before availing leave
                    before_availing_leave = self.get_before_availing_leave(request.POST['leave_type'],
                                                                           request.POST['start_date'],
                                                                           start_time)

                    if before_availing_leave is '':
                        before_availing_data = True
                    else:
                        before_availing_data = False
                        messages.error(self.request, before_availing_leave)

                    # validation for after availing leave

                    leave = LeaveMaster.objects.get(id=request.POST['leave_type'])
                    both_restriction = False
                    if leave.after_availing_leave and leave.before_availing_leave:
                        both_restriction = True
                        if before_availing_data is False:
                            both_restriction = False
                    if both_restriction is False:
                        after_availing_leave = self.get_after_availing_leave(request.POST['leave_type'],
                                                                             request.POST['end_date'],
                                                                             end_time)
                        if after_availing_leave is '':
                            after_availing_data = True
                        else:
                            after_availing_data = False
                            messages.error(self.request, after_availing_leave)

                    # validation for minimum and maximum at a time
                    limit = self.get_limit_at_a_time(query, request.POST['leave_type'],
                                                     request.POST['start_date'],
                                                     request.POST['end_date'], start_time,
                                                     end_time, leave_master.sandwich_leave_allowed)

                    if limit is '':
                        limit_data = True
                    else:
                        limit_data = False
                        messages.error(self.request, limit)

                    # validation for minimum gap
                    gap = get_minimum_gap(query, request.POST['leave_type'],
                                          request.POST['start_date'], start_time)

                    if gap is '':
                        gap_data = True
                    else:
                        gap_data = False
                        messages.error(self.request, gap)

                    # validation for restriction
                    restriction = get_restriction(query, request.POST['leave_type'],
                                                  request.POST['start_date'],
                                                  request.POST['end_date'], start_time,
                                                  end_time, leave_master.sandwich_leave_allowed)
                    if restriction is '':
                        restriction_data = True
                    else:
                        restriction_data = False
                        messages.error(self.request, restriction)

                    if attachment_data is True and \
                        before_availing_data is True and \
                        after_availing_data is True and \
                        remaining_data is True and \
                            limit_data is True and gap_data is True and restriction_data is True:

                        if end_time and ',' in end_time:
                            e_time = end_time.split(',')
                            end_time = e_time[1].strip()

                        form = form.save(commit=False)
                        form.employee_id = query
                        form.leave_type_id = request.POST['leave_type']
                        form.status = 'pending'
                        form.start_time = start_time
                        form.end_time = end_time
                        form.save()

                        Approval(request=request, model=form).set()

                        messages.success(self.request, "Success")

                        return redirect('self_panel:leave_status')
                else:
                    messages.error(self.request, avail_capability)

        return render(request, self.template_name, context)


class LeaveStatusView(LoginRequiredMixin, UserPassesTestMixin, PermissionMixin, ListView):
    """Leave status."""

    template_name = 'self_panel/leave/status.html'
    model = LeaveEntry
    context_object_name = 'leaves'

    def test_func(self):
        return self.request.user.self_panel and self.request.user.employee

    def get_queryset(self):
        return LeaveEntry.objects.filter(employee_id=self.request.user.employee_id, leave_type__status=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        info_qs = get_query_information(self.request.user.employee_id)
        info, leave_list, choices = info_qs

        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['leave_list'] = leave_list
        context['total_leave_applied'] = len(self.object_list)
        context['approved_leave'] = len(list(filter(lambda x: x.status == 'approved', self.object_list)))
        context['declined_leave'] = len(list(filter(lambda x: x.status == 'declined', self.object_list)))
        context['pending_leave'] = len(list(filter(lambda x: x.status == 'pending', self.object_list)))

        return context


class LeaveApplyUpdateView(LoginRequiredMixin, UserPassesTestMixin, PermissionMixin, DetailView):
    """Leave update & comment view."""

    template_name = 'self_panel/leave/edit.html'
    model = LeaveEntry
    context_object_name = 'leave'

    def test_func(self):
        return self.request.user.self_panel and self.request.user.employee

    def get_object(self, queryset=None):
        return get_object_or_404(LeaveEntry, employee_id=self.request.user.employee_id,
                                 leave_type__status=True,
                                 employee=self.request.user.employee)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LeaveApprovalForm()
        context['comments'] = LeaveApprovalComment.objects.filter(leave_entry=self.kwargs['pk'])

        return context

    def post(self, request, *args, **kwargs):
        form = LeaveApprovalForm(request.POST)

        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.leave_entry_id = self.kwargs['pk']
            form.save()
            return redirect('self_panel:leave_update', self.kwargs['pk'])

        return render(request, self.template_name, {
            'leave': self.get_object(),
            'form': form,
            'comments': LeaveApprovalComment.objects.filter(leave_entry=self.kwargs['pk'])
        })


class LeaveDeleteView(LoginRequiredMixin, UserPassesTestMixin, PermissionMixin, DeleteView):
    model = LeaveEntry
    success_url = reverse_lazy('self_panel:leave_status')

    def test_func(self):
        return self.request.user.self_panel and self.request.user.employee

    def get_object(self, queryset=None):
        return get_object_or_404(LeaveEntry, employee_id=self.request.user.employee_id,
                                 leave_type__status=True,
                                 employee=self.request.user.employee)

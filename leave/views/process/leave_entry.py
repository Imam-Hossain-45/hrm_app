from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from leave.forms import *
from django.shortcuts import render, redirect, get_object_or_404
from helpers.mixins import PermissionMixin
from employees.models import EmployeeIdentification, LeaveManage, JobInformation, Employment
from django.contrib import messages
from django.http import JsonResponse
import math
import datetime
from django.db.models import Sum
from django.db.models import Q
from attendance.models import DailyRecord, AttendanceData, ScheduleRecord
from attendance.views import get_late_day_status, get_early_day_status, get_under_work, daily_record
from helpers.functions import get_organizational_structure, get_employee_query_info
from user_management.models import Approval as ApprovalModel
from user_management.workflow import Approval
from django.core.paginator import Paginator


def get_bisect(data, hours_list, day_list, start_time, end_time):
    from bisect import bisect_right
    if data > hours_list[-1]:
        return end_time, 1.00
    else:
        if data in hours_list:
            pos = hours_list.index(data)
            return end_time, day_list[pos]
        else:
            time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
            pos = (bisect_right(hours_list, data))
            end_time = datetime.datetime.strptime(
                start_time, '%H:%M') - time_zero + hours_list[pos]
            leave_time = str(end_time).split(':')
            return leave_time[0] + ':' + leave_time[1], day_list[pos]


#
# def seconds_until_end_of_today(time):
#     time_delta = datetime.datetime.combine(
#         datetime.datetime.now().date() + datetime.timedelta(days=1), datetime.datetime.strptime("0000", "%H%M").time()
#     ) - datetime.datetime.combine(
#             datetime.datetime.now().date(),time)
#     return time_delta.seconds


def get_quarter(day):
    if day.month in [1, 2, 3]:
        start_quarter = datetime.datetime(year=day.year, month=1, day=1)
        end_quarter = datetime.datetime(year=day.year, month=3, day=31)
    elif day.month in [4, 5, 6]:
        start_quarter = datetime.datetime(year=day.year, month=4, day=1)
        end_quarter = datetime.datetime(year=day.year, month=6, day=30)
    elif day.month in [7, 8, 9]:
        start_quarter = datetime.datetime(year=day.year, month=7, day=1)
        end_quarter = datetime.datetime(year=day.year, month=9, day=30)
    else:
        start_quarter = datetime.datetime(year=day.year, month=10, day=1)
        end_quarter = datetime.datetime(year=day.year, month=12, day=31)
    return start_quarter, end_quarter


def get_half_year(day):
    if day.month in [1, 2, 6]:
        start_half = datetime.datetime(year=day.year, month=1, day=1)
        end_half = datetime.datetime(year=day.year, month=6, day=30)
    else:
        start_half = datetime.datetime(year=day.year, month=7, day=1)
        end_half = datetime.datetime(year=day.year, month=12, day=31)
    return start_half, end_half


def EmployeeFilter(employee, from_date, to_date, company, division, department, business_unit, branch, schedule):
    if employee not in ['', None] or from_date not in ['', None] or \
        to_date not in ['', None] or company not in ['', None] or \
        division not in ['', None] or department not in ['', None] or \
            business_unit not in ['', None] or branch not in ['', None] or schedule not in ['', None]:

        object_list = LeaveEntry.objects
        if employee not in ['', None]:
            object_list = object_list.filter(employee=employee)
        if from_date not in ['', None] and to_date not in ['', None]:
            object_list = object_list.filter(
                end_date__gte=from_date).filter(start_date__lte=to_date)
        if company not in ['', None]:
            object_list = object_list.filter(
                employee__employee_job_informations__company=company)
        if division not in ['', None]:
            object_list = object_list.filter(
                employee__employee_job_informations__division=division)
        if department not in ['', None]:
            object_list = object_list.filter(
                employee__employee_job_informations__department=department)
        if business_unit not in ['', None]:
            object_list = object_list.filter(
                employee__employee_job_informations__business_unit=business_unit)
        if schedule not in ['', None]:
            object_list = object_list.filter(
                employee__employee_attendance__schedule_type=schedule)
        return object_list.order_by('-updated_at')
    else:
        return LeaveEntry.objects.filter(leave_type__status=True).order_by('-updated_at')


class LeaveEntryListView(LoginRequiredMixin, PermissionMixin, ListView):
    """
        show individual employee leave entry list
        Access: Super-Admin, Admin
        Url: /admin/leave/leave_entry/list/
    """
    template_name = 'leave/process/entry/list.html'
    model = LeaveEntry
    permission_required = 'view_leaveentry'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        employee = ''
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['search_form'] = SearchForm(self.request.GET)
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')
        company = self.request.GET.get('company')
        division = self.request.GET.get('division')
        department = self.request.GET.get('department')
        business_unit = self.request.GET.get('business_unit')
        branch = self.request.GET.get('branch')
        schedule = self.request.GET.get('schedule')

        if self.request.GET.get('query'):
            employee = self.request.GET.get('employee')

        if employee:
            context['employee'] = get_employee_query_info(employee)

        object_list = EmployeeFilter(employee, from_date, to_date, company, division, department,
                                     business_unit, branch, schedule)

        if object_list:
            paginator = Paginator(object_list, 50)
            page = self.request.GET.get('page')
            context['leave_application'] = paginator.get_page(page)
            index = context['leave_application'].number - 1
            max_index = len(paginator.page_range)
            start_index = index - 0 if index >= 3 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            context['page_range'] = list(paginator.page_range)[start_index:end_index]
            context['path'] = "%s" % "&".join(["%s=%s" % (key, value) for (key, value) in self.request.GET.items()
                                               if not key == 'page'])

        context['objects'] = object_list

        return context


def get_frequency_convert_time_unit(frequency, frequency_number, time_unit, join_date, credit):
    have_credit = ''
    today = datetime.datetime.now()
    next_year = datetime.datetime(year=today.year + 1, month=1, day=1)
    remaining_days = next_year.date() - join_date
    if time_unit == 'hour':
        if frequency == 'day':
            have_credit = credit
        if frequency == 'week':
            # joining day in this week or not
            start_week = today - datetime.timedelta(today.weekday())
            end_week = start_week + \
                       datetime.timedelta(weeks=int(frequency_number))
            if start_week.date() <= join_date <= end_week.date():
                # frequency week convert into day
                remaining_day_this_week = end_week.date() - join_date
                have_credit = (remaining_day_this_week.days *
                               credit) / (int(frequency_number) * 7)
            else:
                have_credit = credit
        if frequency == 'month':
            if today.month == join_date.month and today.year == join_date.year:
                next_month = datetime.datetime(
                    year=today.year, month=today.month + 1, day=1)
                remaining_days = next_month.date() - join_date
                remaining_hours = int(remaining_days.days * 24) * credit
                # frequency month convert into hour
                have_credit = int(remaining_hours) / \
                              (int(frequency_number) * 730.001)
            else:
                have_credit = credit
        if frequency == 'year':
            if today.year == join_date.year:
                next_month = datetime.datetime(
                    year=today.year + int(frequency_number) - 1, month=today.month, day=1)
                remaining_days = next_month.date() - join_date
                remaining_hours = int(remaining_days.days * 24) * credit
                # frequency year convert into hour
                have_credit = int(remaining_hours) / \
                              (int(frequency_number) * 8760)
            else:
                have_credit = credit
        if frequency == 'quarter':
            start_quarter, end_quarter = get_quarter(today)
            if start_quarter.date() <= join_date <= end_quarter.date():
                next_month = datetime.datetime(
                    year=today.year, month=today.month, day=1)
                remaining_days = next_month.date() - join_date
                remaining_hours = int(remaining_days.days * 24) * credit
                # frequency quarter convert into hour
                have_credit = int(remaining_hours) / \
                              (int(frequency_number) * 2190)
            else:
                have_credit = credit
        if frequency == 'half_year':
            start_half, end_half = get_half_year(today)
            if start_half.date() <= join_date <= end_half.date():
                next_month = datetime.datetime(
                    year=today.year, month=today.month, day=1)
                remaining_days = next_month.date() - join_date
                remaining_hours = int(remaining_days.days * 24) * credit
                # frequency half_year convert into hour
                have_credit = int(remaining_hours) / \
                              (int(frequency_number) * 4380)
            else:
                have_credit = credit
    if time_unit == 'day':
        remaining_hours = int(remaining_days.days) * credit
        if frequency == 'day':
            # frequency day convert into day
            have_credit = remaining_hours / (int(frequency_number) * 1)
        if frequency == 'week':
            # joining day in this week or not
            start_week = today - datetime.timedelta(today.weekday())
            end_week = start_week + \
                       datetime.timedelta(weeks=int(frequency_number))
            if start_week.date() <= join_date <= end_week.date():
                # frequency week convert into day
                remaining_day_this_week = end_week.date() - join_date
                have_credit = (remaining_day_this_week.days *
                               credit) / (int(frequency_number) * 7)
            else:
                have_credit = credit
        if frequency == 'month':
            if today.month == join_date.month and today.year == join_date.year:
                next_month = datetime.datetime(
                    year=today.year, month=today.month + int(frequency_number), day=1)
                remaining_days = next_month.date() - join_date
                remaining_hours = int(remaining_days.days) * credit
                # frequency month convert into hour
                have_credit = int(remaining_hours) / \
                              (int(frequency_number) * 30)
            else:
                have_credit = credit
        if frequency == 'year':
            if today.year == join_date.year:
                next_month = datetime.datetime(
                    year=today.year + int(frequency_number) - 1, month=today.month, day=1)
                remaining_days = next_month.date() - join_date
                remaining_hours = int(remaining_days.days) * credit
                # frequency month convert into hour
                have_credit = int(remaining_hours) / \
                              (int(frequency_number) * 365)
            else:
                have_credit = credit
        if frequency == 'quarter':
            start_quarter, end_quarter = get_quarter(today)
            if start_quarter.date() <= join_date <= end_quarter.date():
                next_month = datetime.datetime(
                    year=today.year, month=today.month, day=1)
                remaining_days = next_month.date() - join_date
                remaining_hours = int(remaining_days.days) * credit
                # frequency month convert into hour
                have_credit = int(remaining_hours) / \
                              (int(frequency_number) * 365 / 4)
            else:
                have_credit = credit
        if frequency == 'half_year':
            start_half, end_half = get_half_year(today)
            if start_half.date() <= join_date <= end_half.date():
                next_month = datetime.datetime(
                    year=today.year, month=today.month, day=1)
                remaining_days = next_month.date() - join_date
                remaining_hours = int(remaining_days.days) * credit

                # frequency month convert into hour
                have_credit = int(remaining_hours) / \
                              (int(frequency_number) * 365 / 2)
            else:
                have_credit = credit
    if time_unit == 'week':
        if frequency == 'week':
            # joining day in this week or not
            start_week = today - datetime.timedelta(today.weekday())
            end_week = start_week + \
                       datetime.timedelta(weeks=int(frequency_number))
            if start_week.date() <= join_date <= end_week.date():
                # frequency week convert into day
                remaining_day_this_week = end_week.date() - join_date
                have_credit = (remaining_day_this_week.days *
                               credit) / (int(frequency_number) * 7)
            else:
                have_credit = credit
        if frequency == 'month':
            if today.month == join_date.month and today.year == join_date.year:
                next_month = datetime.datetime(
                    year=today.year, month=today.month + 1, day=1)
                remaining_days = next_month.date() - join_date
                remaining_hours = int(remaining_days.days) * 0.142857 * credit

                # frequency month convert into hour
                have_credit = int(remaining_hours) / \
                              (int(frequency_number) * 4.34524)
            else:
                have_credit = credit
        if frequency == 'year':
            if today.year == join_date.year:
                next_month = datetime.datetime(
                    year=today.year + int(frequency_number) - 1, month=today.month, day=1)
                remaining_days = next_month.date() - join_date
                remaining_hours = int(remaining_days.days) * credit

                # frequency month convert into hour
                have_credit = int(remaining_hours) / \
                              (int(frequency_number) * 52.1429)
            else:
                have_credit = credit
        if frequency == 'quarter':
            start_quarter, end_quarter = get_quarter(today)
            if start_quarter.date() <= join_date <= end_quarter.date():
                next_month = datetime.datetime(
                    year=today.year, month=today.month, day=1)
                remaining_days = next_month.date() - join_date
                remaining_hours = int(remaining_days.days) * credit

                # frequency month convert into hour
                have_credit = int(remaining_hours) / \
                              (int(frequency_number) * 13.03571)
            else:
                have_credit = credit
        if frequency == 'half_year':
            start_half, end_half = get_half_year(today)
            if start_half.date() <= join_date <= end_half.date():
                next_month = datetime.datetime(
                    year=today.year, month=today.month, day=1)
                remaining_days = next_month.date() - join_date
                remaining_hours = int(remaining_days.days) * credit

                # frequency month convert into hour
                have_credit = int(remaining_hours) / \
                              (int(frequency_number) * 26.0714)
            else:
                have_credit = credit
    if time_unit == 'month':
        if frequency == 'month':
            if today.month == join_date.month and today.year == join_date.year:
                next_month = datetime.datetime(
                    year=today.year, month=today.month + int(frequency_number), day=1)
                remaining_days = next_month.date() - join_date
                remaining_hours = int(remaining_days.days) * 0.0333 * credit
                # frequency month convert into hour
                have_credit = int(remaining_hours) / \
                              (int(frequency_number) * 4.34524)
            else:
                have_credit = credit
        if frequency == 'year':
            if today.year == join_date.year:
                next_month = datetime.datetime(
                    year=today.year + int(frequency_number) - 1, month=today.month, day=1)
                remaining_days = next_month.date() - join_date
                remaining_hours = int(remaining_days.days / 30) * credit

                # frequency month convert into hour
                have_credit = int(remaining_hours) / \
                              (int(frequency_number) * 12)
            else:
                have_credit = credit

        if frequency == 'quarter':
            start_quarter, end_quarter = get_quarter(today)
            if start_quarter.date() <= join_date <= end_quarter.date():
                next_month = datetime.datetime(
                    year=today.year, month=today.month, day=1)
                remaining_days = next_month.date() - join_date

                # frequency month convert into hour
                have_credit = int(remaining_days) * credit / \
                              (int(frequency_number) * 12 / 4)
            else:
                have_credit = credit
        if frequency == 'half_year':
            start_half, end_half = get_half_year(today)
            if start_half.date() <= join_date <= end_half.date():
                next_month = datetime.datetime(
                    year=today.year, month=today.month, day=1)
                remaining_days = next_month.date() - join_date

                # frequency month convert into hour
                have_credit = int(remaining_days) * credit / \
                              (int(frequency_number) * 12 / 2)
            else:
                have_credit = credit
    return have_credit


def convert_time_unit_into_seconds(leave, total_remain):
    if leave.time_unit_basis == "hour":
        in_seconds = total_remain * 3600
    elif leave.time_unit_basis == "day":
        in_seconds = total_remain * 24 * 3600
    elif leave.time_unit_basis == "week":
        in_seconds = total_remain * 7 * 24 * 3600
    else:
        in_seconds = total_remain * 30 * 24 * 3600
    return in_seconds


class LeaveIndividualListView(LoginRequiredMixin, PermissionMixin, ListView):
    """
        show individual employee leave entry list
        Access: Super-Admin, Admin
        Url: /admin/leave/leave_entry/list/?query=pk
    """
    template_name = 'leave/process/entry/individual_list.html'
    model = LeaveEntry
    permission_required = 'view_leaveentry'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        mylist = LeaveEntry.objects.filter(employee_id=self.kwargs['pk'], leave_type__status=True)
        context['job'] = mylist.last().employee.employee_job_information.latest('updated_at')
        data = mylist.order_by('created_at')

        if data:
            paginator = Paginator(data, 50)
            page = self.request.GET.get('page')
            context['leave_application'] = paginator.get_page(page)
            index = context['leave_application'].number - 1
            max_index = len(paginator.page_range)
            start_index = index - 0 if index >= 3 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            context['page_range'] = list(paginator.page_range)[start_index:end_index]
            context['path'] = "%s" % "&".join(["%s=%s" % (key, value) for (key, value) in self.request.GET.items()
                                               if not key == 'page'])

        context['objects'] = data

        return context


class LeaveEntryCreateView(LoginRequiredMixin, PermissionMixin, TemplateView):
    """
        Add new Leave entry
        Access: Super-Admin, Admin
        Url: /admin/leave/leave_entry/new
    """
    template_name = 'leave/process/entry/create.html'
    permission_required = ['add_leaveentry', 'change_leaveentry', 'view_leaveentry',
                           'delete_leaveentry']

    def get_query_information(self, query):
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
            leave_remain_qs = LeaveRemaining.objects.filter(
                employee_id=query, status=True, leave__status=True)
            for leave_remain in leave_remain_qs:
                credit = 0
                leave = leave_remain.leave
                try:
                    leave_settings = LeaveGroupSettings.objects.get(
                        leave_name=leave, leave_group=emp.leave_group)
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

                if leave.time_unit_basis == 'hour':
                    total_remain = leave_remain.remaining_in_seconds / 3600
                    # get total avail leave
                    total_avail = int(leave_remain.availing_in_seconds) / 3600
                elif leave.time_unit_basis == 'day':
                    total_remain = (
                                       leave_remain.remaining_in_seconds / 3600) / 24
                    total_avail = int(
                        leave_remain.availing_in_seconds) / 3600 / 24
                elif leave.time_unit_basis == 'week':
                    total_remain = leave_remain.remaining_in_seconds / \
                                   (3600 * 7 * 24)
                    total_avail = int(
                        leave_remain.availing_in_seconds) / (3600 * 7 * 24)
                else:
                    total_remain = leave_remain.remaining_in_seconds / \
                                   (3600 * 30 * 24)
                    total_avail = int(
                        leave_remain.availing_in_seconds) / (3600 * 30 * 24)

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

    def get_instance(self):
        if self.kwargs.get('pk'):
            return get_object_or_404(LeaveEntry, pk=self.kwargs['pk'], status='pending', leave_type__status=True)

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
                job = leave_group.employee.employee_job_information.latest(
                    'updated_at')
                if can_enjoy_unit == 'day':
                    after_joining = job.date_of_joining + \
                                    datetime.timedelta(days=int(can_enjoy))
                elif can_enjoy_unit == 'week':
                    after_joining = job.date_of_joining + \
                                    datetime.timedelta(days=int(can_enjoy) * 7)
                elif can_enjoy_unit == 'month':
                    after_joining = job.date_of_joining + \
                                    datetime.timedelta(days=int(can_enjoy) * 30)
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
            if before_minimum_unit == 'hours':
                if start_time is not None:
                    data = datetime.datetime.combine(datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                                                     datetime.datetime.strptime(start_time,
                                                                                "%H:%M").time()) - datetime.datetime.now()
                else:
                    data = datetime.datetime.strptime(start_date, '%Y-%m-%d') - datetime.datetime.now()

                data = data.total_seconds()
                if 0 <= data < before_minimum * 3600:
                    result = False
            else:
                if start_time is not None:
                    data = datetime.datetime.combine(datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                                                     datetime.datetime.strptime(start_time,
                                                                                "%H:%M").time()) - datetime.datetime.now()
                else:
                    data = datetime.datetime.strptime(
                        start_date, '%Y-%m-%d').date() - datetime.datetime.now().date()

                data = data.total_seconds()
                if before_minimum_unit == 'days' and 0 <= data < before_minimum * 24 * 3600:
                    result = False
                elif before_minimum_unit == 'months' and 0 <= data < before_minimum * 30 * 24 * 3600:
                    result = False

            if before_maximum_unit == 'hours':
                if start_time is not None:
                    data = datetime.datetime.combine(datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                                                     datetime.datetime.strptime(start_time,
                                                                                "%H:%M").time()) - datetime.datetime.now()
                else:
                    data = datetime.datetime.strptime(start_date, '%Y-%m-%d') - datetime.datetime.now()

                data = data.total_seconds()
                if 0 <= data > before_maximum * 3600:
                    result = False
            else:
                if start_time is not None:
                    data = datetime.datetime.combine(datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                                                     datetime.datetime.strptime(start_time,
                                                                                "%H:%M").time()) - datetime.datetime.now()
                else:
                    data = datetime.datetime.strptime(
                        start_date, '%Y-%m-%d').date() - datetime.datetime.now().date()

                data = data.total_seconds()
                if before_maximum_unit == 'days' and 0 <= data > before_maximum * 24 * 3600:
                    result = False
                elif before_maximum_unit == 'months' and 0 <= data > before_maximum * 30 * 24 * 3600:
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

            if after_maximum_unit == 'hours':
                if end_time is not None:
                    data = datetime.datetime.now() - datetime.datetime.combine(
                        datetime.datetime.strptime(end_date, "%Y-%m-%d"),
                        datetime.datetime.strptime(end_time,
                                                   "%H:%M").time())
                else:
                    data = datetime.datetime.now() - datetime.datetime.strptime(end_date, '%Y-%m-%d')

                data = data.total_seconds()
                if data >= 0 and after_maximum * 3600 < data:
                    result = False
            else:
                if end_time is not None:
                    data = datetime.datetime.now() - datetime.datetime.combine(
                        datetime.datetime.strptime(end_date, "%Y-%m-%d"),
                        datetime.datetime.strptime(end_time,
                                                   "%H:%M").time())
                else:
                    data = datetime.datetime.now().date() - datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

                data = data.total_seconds()
                if after_maximum_unit == 'days' and data >= 0 and after_maximum * 24 * 3600 < data:
                    result = False
                elif after_maximum_unit == 'months' and data >= 0 and after_maximum * 30 * 24 * 3600 < data:
                    result = False

            if result is False:
                validation_message = "You can apply within " + \
                                     str(after_maximum) + ' ' + after_maximum_unit + '.'
        return validation_message

    def get_limit_at_a_time(self, query, leave_type, start_date, end_date, start_time, end_time, sandwich_leave):
        validation_message = ''
        leave_group = LeaveManage.objects.get(employee_id=query)
        leave_settings = LeaveGroupSettings.objects.get(
            leave_group=leave_group.leave_group, leave_name_id=leave_type)
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
                    temp_sandwich = get_sandwich_leave(
                        int(query), s_date, e_date)
                    deduct_sandwich = int(temp_sandwich) * 24 * 3600
                else:
                    deduct_sandwich = 0
                data_in_seconds = (int(data.days + 1) *
                                   24 * 3600) - deduct_sandwich
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
                    minimum = int(leave_settings.minimum_enjoy) * \
                              30 * 24 * 3600
                    if minimum > data_in_seconds:
                        data = False
                if leave_settings.maximum_enjoy:
                    maximum = int(leave_settings.maximum_enjoy) * \
                              30 * 24 * 3600
                    if maximum < data_in_seconds:
                        data = False
            if data is False:
                validation_message = "Can apply minimum " + str(
                    leave_settings.minimum_enjoy) + " " + time_unit + " and maximum " + str(
                    leave_settings.maximum_enjoy) + " " + time_unit + " at a time."
            else:
                validation_message = ''
        return validation_message

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        if self.request.GET.get('query'):
            query = self.request.GET.get('query')
        elif self.kwargs.get('employee_id'):
            query = self.kwargs['employee_id']
        else:
            query = None

        if query is not None:
            info_qs = self.get_query_information(query)
            try:
                info, leave_list, choices = info_qs
                context['info'] = info
                context['leave_list'] = leave_list
                context['last_apply_leave_list'] = LeaveEntry.objects.filter(employee_id=query,
                                                                             leave_type__status=True).last()

                if self.get_instance():
                    context['form'] = LeaveEntryForm(choices, initial={'leave_type': self.get_instance().leave_type_id},
                                                     instance=self.get_instance())
                    context['edit'] = True
                else:
                    context['form'] = LeaveEntryForm(choices)
            except TypeError:
                context['error'] = info_qs
        return context

    def post(self, request, *args, **kwargs):
        context = dict()
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        if self.request.GET.get('query'):
            query = self.request.GET.get('query')
        elif self.kwargs.get('employee_id'):
            query = self.kwargs['employee_id']
        else:
            query = None

        if query is not None:
            info, leave_list, choices = self.get_query_information(query)
            context['info'] = info
            context['leave_list'] = leave_list
            context['last_apply_leave_list'] = LeaveEntry.objects.filter(employee_id=query,
                                                                         leave_type__status=True).last()
            if self.get_instance():
                context['form'] = LeaveEntryForm(choices, request.POST, files=request.FILES,
                                                 initial={
                                                     'leave_type': self.get_instance().leave_type_id},
                                                 instance=self.get_instance())
                context['edit'] = True
            else:
                context['form'] = LeaveEntryForm(
                    choices, request.POST, files=request.FILES)

            if request.POST:
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
                    post_dict['start_time'] = post_dict['start_time'].strftime(
                        '%H:%M')
                if self.request.POST.get('end_time').strip() not in ['', None]:
                    post_dict['end_time'] = datetime.datetime.strptime(convert_time(self.request.POST['end_time']),
                                                                       '%I:%M %p')
                    post_dict['end_time'] = post_dict['end_time'].strftime(
                        '%H:%M')
                form = LeaveEntryForm(
                    choices, data=post_dict, files=request.FILES, instance=self.get_instance())

                # if leave type time unit is hour, start time and end time field will required
                try:
                    leave_master = LeaveMaster.objects.get(
                        id=request.POST['leave_type'])
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

                    if request.user.is_superuser or request.user.management:
                        avail_capability = True
                    else:
                        avail_capability = self.get_avail_capability(
                            query, request.POST['leave_type'])

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

                        if request.user.is_superuser or request.user.management:
                            remaining_data = True
                        else:
                            if msg is '':
                                remaining_data = True
                            else:
                                remaining_data = False
                                messages.error(self.request, msg)

                        # validation for document required
                        if request.user.is_superuser or request.user.management:
                            attachment_data = True
                        else:
                            if request.POST.get('attachment') is '':
                                if self.get_leave_information(request.POST['leave_type'], request.POST['start_date'],
                                                              request.POST['end_date'], start_time,
                                                              end_time) is True:
                                    attachment_data = True
                                else:
                                    attachment_data = False
                                    messages.error(
                                        self.request, "The document is required.")
                            else:
                                attachment_data = True

                        # validation for before availing leave
                        if request.user.is_superuser or request.user.management:
                            before_availing_data = True
                        else:
                            before_availing_leave = self.get_before_availing_leave(request.POST['leave_type'],
                                                                                   request.POST['start_date'],
                                                                                   start_time)

                            if before_availing_leave is '':
                                before_availing_data = True
                            else:
                                before_availing_data = False
                                messages.error(
                                    self.request, before_availing_leave)

                        # validation for after availing leave
                        after_availing_data = True
                        if request.user.is_superuser or request.user.management:
                            after_availing_data = True
                        else:
                            leave = LeaveMaster.objects.get(
                                id=request.POST['leave_type'])
                            both_restriction = False
                            if leave.after_availing_leave and leave.before_availing_leave:
                                both_restriction = True
                                if before_availing_data is False:
                                    both_restriction = False
                            print(both_restriction)
                            if both_restriction is False or before_availing_data is False:
                                after_availing_leave = self.get_after_availing_leave(request.POST['leave_type'],
                                                                                     request.POST['end_date'],
                                                                                     end_time)
                                if after_availing_leave is '':
                                    after_availing_data = True
                                else:
                                    after_availing_data = False
                                    messages.error(
                                        self.request, after_availing_leave)

                        # validation for minimum and maximum at a time
                        if request.user.is_superuser or request.user.management:
                            limit_data = True
                        else:
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
                        if request.user.is_superuser or request.user.management:
                            gap_data = True
                        else:
                            gap = get_minimum_gap(query, request.POST['leave_type'],
                                                  request.POST['start_date'], start_time)

                            if gap is '':
                                gap_data = True
                            else:
                                gap_data = False
                                messages.error(self.request, gap)

                        # validation for restriction
                        if request.user.is_superuser or request.user.management:
                            restriction_data = True
                        else:
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

                            if end_time not in ['', None] and ',' in end_time:
                                e_time = end_time.split(',')
                                end_time = e_time[1].strip()

                            form = form.save(commit=False)
                            form.employee_id = query
                            form.leave_type_id = request.POST['leave_type']

                            if 'apply' in request.POST:
                                form.status = 'pending'
                                form.start_time = start_time
                                form.end_time = end_time
                                form.save()
                            elif 'apply_approve' in request.POST:
                                form.status = 'approved'
                                form.start_time = start_time
                                form.end_time = end_time
                                form.save()
                                LeaveAvail.objects.create(employee_id=query,
                                                          avail_leave_id=request.POST['leave_type'],
                                                          credit_seconds=availing,
                                                          start_date=request.POST['start_date'],
                                                          end_date=request.POST['end_date'],
                                                          start_time=form.start_time,
                                                          end_time=form.end_time,
                                                          notes='Approved this leave')
                                LeaveRemaining.objects.update_or_create(employee_id=int(query),
                                                                        leave_id=request.POST['leave_type'],
                                                                        status=True,
                                                                        defaults={
                                                                            'remaining_in_seconds': remain_leave,
                                                                            'availing_in_seconds': total_avail,
                                                                        })
                                set_daily_record(query, request.POST['start_date'], request.POST['end_date'],
                                                 leave_master.paid, leave_master, availing,
                                                 leave_master.sandwich_leave_allowed)

                            else:
                                form.status = 'declined'
                                form.start_time = start_time
                                form.end_time = end_time
                                form.save()
                            messages.success(self.request, "Success")
                            return redirect('beehive_admin:leave:leave_entry_list')
                    else:
                        messages.error(self.request, avail_capability)
        return render(request, self.template_name, context)


class LeaveEntryDetailsView(LoginRequiredMixin, PermissionMixin, DetailView):
    template_name = 'leave/process/entry/details.html'
    permission_required = 'view_leaveentry'
    model = LeaveEntry

    def get_query_information(self, query):
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
            leave_remain_qs = LeaveRemaining.objects.filter(
                employee_id=query, status=True, leave__status=True)
            for leave_remain in leave_remain_qs:
                credit = 0
                leave = leave_remain.leave
                try:
                    leave_settings = LeaveGroupSettings.objects.get(
                        leave_name=leave, leave_group=emp.leave_group)
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

                if leave.time_unit_basis == 'hour':
                    total_remain = leave_remain.remaining_in_seconds / 3600
                    # get total avail leave
                    total_avail = int(leave_remain.availing_in_seconds) / 3600
                elif leave.time_unit_basis == 'day':
                    total_remain = (
                                       leave_remain.remaining_in_seconds / 3600) / 24
                    total_avail = int(
                        leave_remain.availing_in_seconds) / 3600 / 24
                elif leave.time_unit_basis == 'week':
                    total_remain = leave_remain.remaining_in_seconds / \
                                   (3600 * 7 * 24)
                    total_avail = int(
                        leave_remain.availing_in_seconds) / (3600 * 7 * 24)
                else:
                    total_remain = leave_remain.remaining_in_seconds / \
                                   (3600 * 30 * 24)
                    total_avail = int(
                        leave_remain.availing_in_seconds) / (3600 * 30 * 24)

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

    def get_instance(self):
        if self.kwargs.get('pk'):
            return LeaveEntry.objects.get(id=self.kwargs['pk'], status__in=['declined', 'approved'],
                                          leave_type__status=True)

    def get_leave_information(self):
        leave = self.get_instance()
        if leave.start_time is not None and leave.end_time is not None:
            combine_start_date_time = datetime.datetime.combine(
                leave.start_date, leave.start_time)
            combine_end_date_time = datetime.datetime.combine(
                leave.end_date, leave.end_time)
            credit = combine_end_date_time - combine_start_date_time
        else:
            end_date = datetime.datetime(year=leave.end_date.year, month=leave.end_date.month,
                                         day=leave.end_date.day) + datetime.timedelta(days=1)
            start_date = datetime.datetime(year=leave.start_date.year, month=leave.start_date.month,
                                           day=leave.start_date.day)
            credit = (end_date - start_date)

        data = {
            'name': leave.leave_type,
            'credit': credit,
            'start_date': leave.start_date,
            'start_time': leave.start_time,
            'end_date': leave.end_date,
            'end_time': leave.end_time,
            'apply_date': leave.created_at,
            'reason': leave.reason_of_leave,
            'attachment': leave.attachment,
            'attachment_url': leave.attachment.url if leave.attachment else '',
            'status': leave.get_status_display(),
        }
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        if self.request.GET.get('query'):
            query = self.request.GET.get('query')
        elif self.kwargs.get('employee_id'):
            query = self.kwargs['employee_id']
        else:
            query = None

        if query is not None:
            info_qs = self.get_query_information(query)
            try:
                info, leave_list, choices = info_qs
                context['info'] = info
                context['leave_list'] = leave_list
                context['leave_info'] = self.get_leave_information()
                context['comment'] = LeaveApprovalComment.objects.filter(
                    leave_entry=self.kwargs['pk'])
                context['last_apply_leave_list'] = LeaveEntry.objects.filter(employee_id=query,
                                                                             leave_type__status=True).last()
            except TypeError:
                context['error'] = info_qs
        return context


def get_sandwich_leave(em, s_date, e_date):
    # check for working date or not
    schedule_record_qs = ScheduleRecord.objects.filter(employee=em)
    d = e_date - s_date
    day = 0
    for i in range(d.days + 1):
        temp = s_date + datetime.timedelta(days=i)
        try:
            schedule_record_qs.get(date=temp.date(), is_working_day=False)
            day = day + 1
        except:
            day = day + 0
    return day


def get_remaining_leave(query, leave_type, start_date, end_date, start_time, end_time, sandwich_leave):
    """
        Remaining leave for a employee
    """
    validation_message = ''
    remain_leave = LeaveRemaining.objects.get(
        employee_id=int(query), leave_id=int(leave_type), status=True)
    remaining = remain_leave.remaining_in_seconds
    total_avail = remain_leave.availing_in_seconds
    if start_time is not None and end_time is not None:
        leave_master = LeaveMaster.objects.get(id=leave_type)
        # total hour (end time - start time)
        data = datetime.datetime.combine(
            datetime.datetime.strptime(str(end_date), "%Y-%m-%d"),
            datetime.datetime.strptime(end_time, '%H:%M').time()
        ) - \
               datetime.datetime.combine(
                   datetime.datetime.strptime(str(start_date), "%Y-%m-%d"),
                   datetime.datetime.strptime(start_time, '%H:%M').time()
               )
        if data.total_seconds() < 0:
            validation_message = "Please enter a valid time."
            availing = 0
            return end_time, availing, remaining, total_avail, validation_message

        days, hours, minutes, seconds = data.days, data.seconds // 3600, data.seconds // 60 % 60, data.seconds % 60
        split_time = datetime.timedelta(
            hours=hours, minutes=minutes, seconds=seconds)
        day_leave = days * 24 * 3600
        data = data.total_seconds()
        if leave_master.partial_leave_allowed:
            hours_list = []
            day_list = []
            for partial in leave_master.partial_leave.all():
                hours, min = str(partial.partial_leave_hours).split('.')
                leave_hours = datetime.timedelta(
                    hours=int(hours), minutes=int(min))
                hours_list.append(leave_hours)
                day_list.append(partial.partial_leave_day)
            leave_time, leave_day = get_bisect(
                split_time, hours_list, day_list, start_time, end_time)
            end_time = str(leave_time)
            availing = day_leave + (leave_day * 24 * 3600)
        else:
            availing = 0
            # for fractional leave calculation
            if leave_master.fractional:
                unit = leave_master.fractional_time_unit
                leave_group = LeaveManage.objects.get(employee_id=query)
                duration = LeaveGroupSettings.objects.get(
                    leave_group=leave_group.leave_group, leave_name_id=leave_type)

                if unit == 'minutes':
                    duration_in_seconds = duration.fractional_duration * 60
                else:
                    duration_in_seconds = duration.fractional_duration * 60 * 60
                try:
                    dividend = int(data / duration_in_seconds)
                except ZeroDivisionError:
                    dividend = data
                try:
                    fraction = data % duration_in_seconds
                except ZeroDivisionError:
                    fraction = data

                if fraction > 0:
                    dividend += 1

                total_fraction = dividend * duration_in_seconds
                time_zero = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
                end_time = str(datetime.datetime.strptime(start_time, '%H:%M') - time_zero + datetime.timedelta(
                    seconds=total_fraction))
                availing = total_fraction

    else:
        s_date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d')
        e_date = datetime.datetime.strptime(str(end_date), '%Y-%m-%d')
        if sandwich_leave is False:
            temp_sandwich = get_sandwich_leave(int(query), s_date, e_date)
            deduct_sandwich = int(temp_sandwich) * 24 * 3600
        else:
            deduct_sandwich = 0

        data = e_date - s_date
        availing = (int(data.days + 1) * 24 * 3600) - deduct_sandwich
        end_time = None
    if remaining < availing:
        validation_message = "The leave limit is over."
    else:
        remaining = remaining - availing
    total_avail = int(total_avail) + int(availing)
    return end_time, availing, remaining, total_avail, validation_message


def get_minimum_gap(query, leave_type, start_date, start_time):
    validation_message = ''
    leave_group = LeaveManage.objects.get(employee_id=query)
    leave_settings = LeaveGroupSettings.objects.get(
        leave_group=leave_group.leave_group, leave_name_id=leave_type)
    if leave_settings.leave_gap:
        approved_leave = LeaveEntry.objects.filter(employee_id=int(query), leave_type_id=leave_type,
                                                   status='approved', leave_type__status=True).last()
        if approved_leave:
            approve_end_date = approved_leave.end_date
            approve_end_time = approved_leave.end_time
            if start_time is not None and approve_end_time is not None:
                data = datetime.datetime.combine(datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                                                 datetime.datetime.strptime(start_time,
                                                                            "%H:%M").time()) - datetime.datetime.combine(
                    approve_end_date,
                    datetime.datetime.strptime(approve_end_time,
                                               "%H:%M").time())
                data_in_seconds = data.total_seconds()
            else:
                data = datetime.datetime.strptime(
                    start_date, '%Y-%m-%d').date() - approve_end_date
                data_in_seconds = int(data.days + 1) * 24 * 3600
            gap = leave_settings.minimum_gap
            gap_unit = leave_settings.minimum_gap_unit
            if gap_unit == 'day':
                gap_in_seconds = int(gap) * 24 * 3600
            elif gap_unit == 'week':
                gap_in_seconds = int(gap) * 7 * 24 * 3600
            elif gap_unit == 'month':
                gap_in_seconds = int(gap) * 30 * 24 * 3600
            else:
                gap_in_seconds = int(gap) * 365 * 24 * 3600
            if gap_in_seconds >= data_in_seconds:
                validation_message = "The minimum leave gap is " + \
                                     str(gap) + " " + gap_unit
    return validation_message


def get_restriction(query, leave_type, start_date, end_date, start_time, end_time, sandwich_leave):
    """
        Count leave for restriction
    """
    leave_master = LeaveMaster.objects.get(id=leave_type)
    if start_time is not None and end_time is not None:
        if start_date == end_date:
            data = datetime.datetime.strptime(
                end_time, "%H:%M:%S") - datetime.datetime.strptime(start_time, '%H:%M')
            split_time = data
            day_leave = 0
            data = data.total_seconds()
        else:
            datetime.datetime.strptime(end_time,
                                       "%H:%M:%S")
            data = datetime.datetime.combine(datetime.datetime.strptime(str(end_date), "%Y-%m-%d"),
                                             datetime.datetime.strptime(end_time,
                                                                        "%H:%M:%S").time()) - datetime.datetime.combine(
                datetime.datetime.strptime(str(start_date), "%Y-%m-%d"),
                datetime.datetime.strptime(start_time, "%H:%M").time())
            days, hours, minutes, seconds = data.days, data.seconds // 3600, data.seconds // 60 % 60, data.seconds % 60
            split_time = datetime.timedelta(
                hours=hours, minutes=minutes, seconds=seconds)
            day_leave = days * 24 * 3600
            data = data.total_seconds()
        if leave_master.partial_leave_allowed:
            hours_list = []
            day_list = []
            for partial in leave_master.partial_leave.all():
                hours, min = str(partial.partial_leave_hours).split('.')
                leave_hours = datetime.timedelta(
                    hours=int(hours), minutes=int(min))
                hours_list.append(leave_hours)
                day_list.append(partial.partial_leave_day)
            leave_time, leave_day = get_bisect(
                split_time, hours_list, day_list, start_time, end_time)
            new_leave = day_leave + (leave_day * 24 * 3600)
        else:
            new_leave = 0
            # for fractional leave calculation
            if leave_master.fractional:
                unit = leave_master.fractional_time_unit
                leave_group = LeaveManage.objects.get(employee_id=query)
                duration = LeaveGroupSettings.objects.get(
                    leave_group=leave_group.leave_group, leave_name_id=leave_type)
                if unit == 'minutes':
                    duration_in_seconds = duration.fractional_duration * 60
                else:
                    duration_in_seconds = duration.fractional_duration * 60 * 60
                fraction = data // duration_in_seconds
                if data % duration_in_seconds > 0:
                    fraction = fraction + 1
                new_leave = fraction * duration_in_seconds

    else:
        s_date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d')
        e_date = datetime.datetime.strptime(str(end_date), '%Y-%m-%d')
        if sandwich_leave is False:
            temp_sandwich = get_sandwich_leave(int(query), s_date, e_date)
            deduct_sandwich = int(temp_sandwich) * 24 * 3600
        else:
            deduct_sandwich = 0

        data = e_date - s_date
        new_leave = (int(data.days + 1) * 24 * 3600) - deduct_sandwich
    avail_leave = LeaveAvail.objects.filter(
        employee_id=query, avail_leave_id=leave_type, status=1)

    validation_message = ''
    leave_group = LeaveManage.objects.get(employee_id=query)
    leave_settings = LeaveGroupSettings.objects.get(
        leave_group=leave_group.leave_group, leave_name_id=leave_type)
    if start_time is not None:
        start_date = datetime.datetime.combine(datetime.datetime.strptime(str(start_date), "%Y-%m-%d"),
                                               datetime.datetime.strptime(start_time, "%H:%M").time())
    else:
        start_date = datetime.datetime.strptime(str(start_date), "%Y-%m-%d")

    for restrict in leave_settings.leave_restriction.all():
        if restrict.within_unit == "day":
            date_N_days_ago = start_date - \
                              datetime.timedelta(days=restrict.within - 1)
        elif restrict.within_unit == "week":
            date_N_days_ago = start_date - \
                              datetime.timedelta(days=restrict.within * 7 - 1)
        elif restrict.within_unit == "month":
            date_N_days_ago = start_date - \
                              datetime.timedelta(days=restrict.within * 30)
        elif restrict.within_unit == "year":
            date_N_days_ago = start_date - \
                              datetime.timedelta(days=restrict.within * 365)
        elif restrict.within_unit == "quarter":
            date_N_days_ago = start_date - \
                              datetime.timedelta(days=restrict.within * 365 / 4)
        else:
            date_N_days_ago = start_date - \
                              datetime.timedelta(days=restrict.within * 365 / 2)

        avail_leave_count = avail_leave.filter(start_date__lte=start_date, end_date__gte=date_N_days_ago).aggregate(
            Sum('credit_seconds'))
        if avail_leave_count['credit_seconds__sum'] is None:
            credit_seconds_sum = 0
        else:
            credit_seconds_sum = avail_leave_count['credit_seconds__sum']
        total_leave_this_period = credit_seconds_sum + new_leave
        if leave_master.time_unit_basis == 'day':
            can_enjoy = restrict.can_enjoy * 24 * 3600
        elif leave_master.time_unit_basis == 'hour':
            can_enjoy = restrict.can_enjoy * 3600
        elif leave_master.time_unit_basis == 'week':
            can_enjoy = restrict.can_enjoy * 24 * 7 * 3600
        else:
            can_enjoy = restrict.can_enjoy * 24 * 30 * 3600
        if total_leave_this_period > can_enjoy:
            return 'Can enjoy' + ' ' + str(restrict.can_enjoy) + ' ' + str(leave_master.time_unit_basis) + ' ' + str(
                leave_master.name) + ' ' + 'within' + ' ' + str(restrict.within) + ' ' + str(restrict.within_unit) + '.'

    return validation_message


class LeaveEntrySearchView(LoginRequiredMixin, PermissionMixin, TemplateView):
    """
        Search result by ajax
    """

    def get(self, request, *args):
        query = request.GET.get('search_text')
        employee_list = []
        data = dict()
        if query not in EMPTY_VALUES:
            results = EmployeeIdentification.objects.filter(Q(first_name__icontains=query) | Q(
                middle_name__icontains=query) | Q(last_name__icontains=query))
            if not results:
                results = EmployeeIdentification.objects.filter(
                    employee_id__istartswith=query)
            employee_dict = dict()
            for result in results:
                employee_dict['id'] = result.id
                employee_dict[
                    'name'] = result.get_title_display() + ' ' + result.first_name + ' ' + result.middle_name + ' ' + result.last_name
                employee_dict['employee_id'] = result.employee_id or ''
                try:
                    job = JobInformation.objects.filter(
                        employee=result).latest('updated_at')
                    designation = job.designation.name
                except:
                    designation = ' '
                employee_dict['designation'] = designation
                employee_list.append(dict(employee_dict))
        data['employee_list'] = employee_list
        return JsonResponse(data)


class LeavePendingListView(LoginRequiredMixin, PermissionMixin, ListView):
    """
        show pending leave list
        Access: Super-Admin, Admin
        Url: /admin/leave/leave_approval/list/
    """
    template_name = 'leave/process/approval/list.html'
    model = LeaveEntry
    permission_required = 'view_leaveentry'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = ''

        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['search_form'] = SearchForm(self.request.GET)
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')
        company = self.request.GET.get('company')
        division = self.request.GET.get('division')
        department = self.request.GET.get('department')
        business_unit = self.request.GET.get('business_unit')
        branch = self.request.GET.get('branch')
        schedule = self.request.GET.get('schedule')

        if self.request.GET.get('query'):
            employee = self.request.GET.get('employee')

        if employee:
            context['employee'] = get_employee_query_info(employee)

        if employee not in ['', None] or from_date not in ['', None] or \
            to_date not in ['', None] or company not in ['', None] or division not in ['', None] or \
            department not in ['', None] or business_unit not in ['', None] or \
            branch not in ['', None] or schedule not in ['', None]:
            object_list = LeaveEntry.objects.filter(status='pending', leave_type__status=True)
            if employee not in ['', None]:
                object_list = object_list.filter(employee=employee)
            if from_date not in ['', None] and to_date not in ['', None]:
                object_list = object_list.filter(
                    Q(start_date__gte=from_date) | Q(end_date__lte=to_date))
            if company not in ['', None]:
                object_list = object_list.filter(
                    employee__employee_job_informations__company=company)
            if division not in ['', None]:
                object_list = object_list.filter(
                    employee__employee_job_informations__division=division)
            if department not in ['', None]:
                object_list = object_list.filter(
                    employee__employee_job_informations__department=department)
            if business_unit not in ['', None]:
                object_list = object_list.filter(
                    employee__employee_job_informations__business_unit=business_unit)
            if schedule not in ['', None]:
                object_list = object_list.filter(
                    employee__employee_attendance__schedule_type=schedule)
            data = object_list.order_by('created_at')
        else:
            data = LeaveEntry.objects.filter(
                status='pending', leave_type__status=True).order_by('created_at')

        if data:
            paginator = Paginator(data, 50)
            page = self.request.GET.get('page')
            context['leave_application'] = paginator.get_page(page)
            index = context['leave_application'].number - 1
            max_index = len(paginator.page_range)
            start_index = index - 0 if index >= 3 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            context['page_range'] = list(paginator.page_range)[start_index:end_index]
            context['path'] = "%s" % "&".join(["%s=%s" % (key, value) for (key, value) in self.request.GET.items()
                                               if not key == 'page'])

        context['objects'] = data

        return context


class LeaveApprovalView(LoginRequiredMixin, PermissionMixin, TemplateView):
    """
        Add new Leave entry
        Access: Super-Admin, Admin
        Url: /admin/leave/leave_entry/new
    """
    template_name = 'leave/process/approval/create.html'
    permission_required = 'change_leaveentry'

    def get_employee_information(self):
        emp = self.get_instance()
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
        return information

    def get_leave_information(self):
        leave = self.get_instance()
        if leave.start_time is not None and leave.end_time is not None:
            combine_start_date_time = datetime.datetime.combine(
                leave.start_date, leave.start_time)
            combine_end_date_time = datetime.datetime.combine(
                leave.end_date, leave.end_time)
            credit = combine_end_date_time - combine_start_date_time
        else:
            end_date = datetime.datetime(year=leave.end_date.year, month=leave.end_date.month,
                                         day=leave.end_date.day) + datetime.timedelta(days=1)
            start_date = datetime.datetime(year=leave.start_date.year, month=leave.start_date.month,
                                           day=leave.start_date.day)
            credit = (end_date - start_date)

        data = {
            'name': leave.leave_type,
            'credit': credit,
            'start_date': leave.start_date,
            'start_time': leave.start_time,
            'end_date': leave.end_date,
            'end_time': leave.end_time,
            'apply_date': leave.created_at,
            'reason': leave.reason_of_leave,
            'attachment': leave.attachment,
            'attachment_url': leave.attachment.url if leave.attachment else '',
        }
        return data

    def get_instance(self):
        return get_object_or_404(LeaveEntry, id=self.kwargs['pk'], status='pending', leave_type__status=True)
        # return LeaveEntry.objects.get(id=self.kwargs['pk'], status='pending')

    def get_comment(self):
        return LeaveApprovalComment.objects.filter(leave_entry=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        entry = self.kwargs.get('pk')
        if entry is not None:
            context['employee_info'] = self.get_employee_information()
            context['leave_info'] = self.get_leave_information()
            context['form'] = LeaveApprovalForm()
            context['comment'] = self.get_comment()
        return context

    def post(self, request, *args, **kwargs):
        context = dict()
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        entry = self.kwargs.get('pk')
        leave_info = ''

        if entry is not None:
            context['employee_info'] = self.get_employee_information()
            leave_info = self.get_leave_information()
            context['leave_info'] = leave_info
            context['form'] = LeaveApprovalForm(request.POST)
            context['comment'] = self.get_comment()

        if 'save_comment' in request.POST:
            form = LeaveApprovalForm(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                form.user = request.user
                form.leave_entry_id = entry
                form.save()
                return redirect('beehive_admin:leave:leave_approval_form', entry)

        if 'decline' in request.POST:
            leave = LeaveEntry.objects.filter(id=entry)
            approval = Approval(request)
            approval.approve_or_decline('declined', 'leave', entry)

            approvals = ApprovalModel.objects.filter(
                item=entry,
                item_type='leave'
            )
            declined_approvals = list(
                filter(lambda approval: approval.status == 'declined', approvals))

            if approvals.count() == len(declined_approvals):
                LeaveEntry.objects.filter(id=entry).update(status='declined')

                approval.set_notifications(
                    notification_for=entry,
                    content=leave.last().leave_type.__str__() + ' declined for ' + str(leave.last().end_date)
                    if leave.last().start_date == leave.last().end_date
                    else leave.last().leave_type.__str__() + ' declined from ' + str(leave.last().start_date)
                         + ' to ' + str(leave.last().end_date)
                )

            return redirect('beehive_admin:leave:leave_entry_list')

        if 'approve' in request.POST:
            leave_code = LeaveMaster.objects.get(id=leave_info.get('name').id)

            # validation for remaining leave
            td_start = leave_info.get('start_time')
            instance_data = self.get_instance()
            if td_start is not None:
                split_start_time = str(td_start).split(":")
                start_time = split_start_time[0] + ":" + split_start_time[1]
            else:
                start_time = None
            td_end = leave_info.get('end_time')
            if td_end is not None:
                split_end_time = str(td_end).split(":")
                end_time = split_end_time[0] + ":" + split_end_time[1]
            else:
                end_time = None

            end_time, availing, remain_leave, total_avail, msg = get_remaining_leave(instance_data.employee_id,
                                                                                     leave_info.get(
                                                                                         'name').id,
                                                                                     leave_info.get(
                                                                                         'start_date'),
                                                                                     leave_info.get(
                                                                                         'end_date'),
                                                                                     start_time, end_time,
                                                                                     leave_code.sandwich_leave_allowed)
            if request.user.is_superuser or request.user.management:
                remaining_data = True
            else:
                if msg is '':
                    remaining_data = True
                else:
                    remaining_data = False
                    messages.error(self.request, msg)

            # validation for minimum gap
            if request.user.is_superuser or request.user.management:
                gap_data = True
            else:
                gap = get_minimum_gap(instance_data.employee_id, leave_info.get('name').id,
                                      leave_info.get('start_date'),
                                      leave_info.get('start_time'))
                if gap is '':
                    gap_data = True
                else:
                    gap_data = False
                    messages.error(self.request, gap)

            # validation for restriction
            if request.user.is_superuser or request.user.management:
                restriction_data = True
            else:
                restriction = get_restriction(instance_data.employee_id, leave_info.get('name').id,
                                              leave_info.get('start_date'),
                                              leave_info.get(
                                                  'end_date'), start_time,
                                              end_time, leave_code.sandwich_leave_allowed)
                if restriction is '':
                    restriction_data = True
                else:
                    restriction_data = False
                    messages.error(self.request, restriction)

            if remaining_data is True and gap_data is True and restriction_data is True:
                leave = LeaveEntry.objects.filter(id=entry)
                approval = Approval(request)

                approval.approve_or_decline('approved', 'leave', entry)

                approvals = ApprovalModel.objects.filter(
                    item=entry,
                    item_type='leave'
                )
                approved_approvals = list(
                    filter(lambda approval: approval.status == 'approved', approvals))

                if approvals.count() == len(approved_approvals):
                    LeaveAvail.objects.create(employee=instance_data.employee,
                                              avail_leave=leave_info.get(
                                                  'name'),
                                              credit_seconds=availing,
                                              start_date=leave_info.get(
                                                  'start_date'),
                                              end_date=leave_info.get(
                                                  'end_date'),
                                              start_time=leave_info.get(
                                                  'start_time'),
                                              end_time=leave_info.get(
                                                  'end_time'),
                                              notes='Approved this leave')

                    LeaveRemaining.objects.update_or_create(employee=instance_data.employee,
                                                            leave_id=leave_info.get(
                                                                'name'),
                                                            status=True,
                                                            defaults={
                                                                'remaining_in_seconds': remain_leave,
                                                                'availing_in_seconds': total_avail
                                                            })
                    leave.update(status='approved')
                    set_daily_record(instance_data.employee.id, leave_info.get('start_date'),
                                     leave_info.get(
                                         'end_date'), leave_code.paid, leave_code, availing,
                                     leave_code.sandwich_leave_allowed)
                    approval.set_notifications(
                        notification_for=entry,
                        content=leave.last().leave_type.__str__() + ' approved for ' + str(leave.last().end_date)
                        if leave.last().start_date == leave.last().end_date
                        else ' from ' + str(leave.last().start_date) + ' to ' + str(leave.last().end_date)
                    )

                return redirect('beehive_admin:leave:leave_entry_list')
        return render(request, self.template_name, context)


def set_daily_record(em, start_date, end_date, paid, leave_code, availing, sandwich_leave):
    if start_date not in ['', None] and end_date not in ['', None]:
        s_date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d')
        e_date = datetime.datetime.strptime(str(end_date), '%Y-%m-%d')
        d = e_date - s_date

        for i in range(d.days + 1):
            date = s_date + datetime.timedelta(days=i)

            """Save data in ScheduleRecord and DailyRecord"""
            daily_record_data = {
                'employee': em,
                'date': date.date()
            }

            daily_record.set_daily_record(daily_record_data)

            """ get ScheduleRecord or not """
            try:
                schedule_record_qs = ScheduleRecord.objects.filter(employee_id=em, date=date)

                if sandwich_leave is False and schedule_record_qs[0].is_working_day is False:
                    continue

                if schedule_record_qs[0].working_hour > 0:
                    if schedule_record_qs[0].working_hour_unit == 'hour':
                        working_hour = schedule_record_qs[0].working_hour - (
                            availing / 3600)
                    else:
                        working_hour = schedule_record_qs[0].working_hour - (
                            availing / 60)
                    if schedule_record_qs[0].working_hour < 0:
                        working_hour = 0
                else:
                    working_hour = 0

                schedule_record_qs.update(is_leave=True, working_hour=working_hour)
                daily_record_qs = DailyRecord.objects.filter(schedule_record=schedule_record_qs[0])

                if daily_record_qs[0].late or daily_record_qs[0].early or daily_record_qs[0].under_work:
                    attendance_qs = AttendanceData.objects.get(employee_id=em, date=date)
                    is_late, late_value, is_present, daily_pre_overtime_seconds = \
                        get_late_day_status(em, date, attendance_qs.in_time)

                    if attendance_qs.out_date is not None:
                        is_early_out, early_out_value, daily_work_seconds, is_overtime, daily_post_overtime_seconds = \
                            get_early_day_status(em, date, attendance_qs.in_time,
                                                 attendance_qs.out_time, attendance_qs.out_date)
                        is_under_work, under_work_value = get_under_work(
                            em, attendance_qs.daily_work_seconds)
                    else:
                        is_early_out = False
                        early_out_value = 0
                        daily_work_seconds = 0
                        is_overtime = False
                        daily_post_overtime_seconds = 0
                        is_under_work = False
                        under_work_value = 0

                    daily_record_qs.update(late=is_late, late_value=late_value, is_present=is_present,
                                           early=is_early_out,
                                           early_out_value=early_out_value, daily_working_seconds=daily_work_seconds,
                                           is_overtime=is_overtime,
                                           daily_post_overtime_seconds=daily_post_overtime_seconds,
                                           under_work=is_under_work, under_work_value=under_work_value,
                                           is_leave_paid=paid, leave_master=leave_code)
                else:
                    daily_record_qs.update(
                        is_leave_paid=paid, leave_master=leave_code)
            except Exception as e:
                raise e
    return True

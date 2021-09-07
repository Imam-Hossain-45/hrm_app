from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView
from django.db.models import Sum
from django.http import Http404, JsonResponse
from django.db.models.functions import TruncMonth

from attendance.models import ScheduleRecord, AttendanceData, DailyRecord
from dashboard.models import NoticeBoard
from employees.models import EmployeeIdentification, LeaveManage, Attendance, Personal
from leave.models import LeaveRemaining, LeaveGroupSettings
from leave.views import get_frequency_convert_time_unit
from payroll.models import EmployeeSalary, EmployeeVariableSalary
from user_management.workflow import Approval
from datetime import datetime, timedelta
from leave.models import LeaveMaster
from helpers.mixins import PermissionMixin
import math


def map_for_approval(approval):
    """Support for map method from `get_approval` method."""

    duration = 0

    print(approval.item_type)

    if approval.item_type == 'late-entry':
        duration = ScheduleRecord.objects.get(
            employee=approval.content_object.attendance.employee,
            date=approval.content_object.attendance.date
        ).dailyrecord.late_value

    if approval.item_type == 'early-out':
        duration = ScheduleRecord.objects.get(
            employee=approval.content_object.employee,
            date=approval.content_object.attendance.date
        ).dailyrecord.early_out_value

    if approval.item_type == 'leave':
        duration = approval.content_object.duration()

    return {
        'id': approval.id,
        'application_id': approval.item,
        'application_type': approval.item_type,
        'reporting': approval.reporting.__str__(),
        'applied_by': approval.content_object.attendance.employee.__str__()
        if approval.item_type == 'late-entry'
        else approval.content_object.employee.__str__(),
        'applied_for': approval.content_object.leave_type.__str__() if approval.item_type == 'leave' else approval.
        content_object.attendance.employee.__str__(),
        'application_start_date': approval.content_object.start_date if approval.item_type == 'leave' else approval.
        content_object.attendance.date,
        'application_start_time': approval.content_object.start_time if approval.item_type == 'leave' else approval.
        content_object.attendance.date,
        'application_end_date': approval.content_object.end_date if approval.item_type == 'leave' else approval.
        content_object.attendance.date,
        'application_end_time': approval.content_object.end_time if approval.item_type == 'leave' else approval.
        content_object.attendance.date,
        'duration': duration,
        'status': approval.status,
        'status_display': approval.get_status_display(),
        'created_at': approval.created_at,
        'updated_at': approval.updated_at
    }


def set_noticeboard(data=None):
    """ farzana & imam: Set notice for the user. """

    notice_board_qs = NoticeBoard.objects.filter(user=data['user'])
    if not notice_board_qs.exists():
        try:
            attendance = Attendance.objects.get(
                employee=data['employee']).calendar_master
            if attendance and attendance.holiday_group:
                holiday_master = attendance.holiday_group.holiday.\
                    filter(
                        status=True, end_date__gte=data['today_date'], start_date__lte=data['buffer_date'])

                for holiday in holiday_master:
                    NoticeBoard.objects.create(
                        user=data['user'],
                        notice=holiday.name,
                        description=holiday.description,
                        start_date=holiday.start_date,
                        end_date=holiday.end_date,
                        holiday_id=holiday.id,
                        published_datetime=datetime.now()
                    )

        except:
            pass

        # For birthday
        try:
            personal_obj = Personal.objects.get(employee=data['employee'])
            if data['today_date'].day == personal_obj.date_of_birth.day and data['today_date'].month == personal_obj.date_of_birth.month:
                NoticeBoard.objects.create(
                    user=data['user'],
                    notice='Happy Birthday!',
                    start_date=data['today_date'],
                    end_date=data['today_date'],
                    published_datetime=datetime.now(),
                    type='birthday'
                )
        except:
            pass
    else:
        last_holiday_notice_obj = notice_board_qs.filter(
            type='calendar').last()

        try:
            attendance = Attendance.objects.get(
                employee=data['employee']).calendar_master
            if attendance and attendance.holiday_group:
                holiday_master_prev = attendance.holiday_group.holiday.\
                    filter(status=True, id__gt=last_holiday_notice_obj.holiday_id, start_date__lte=data['buffer_date'],
                           end_date__lt=data['today_date'])

                for holiday in holiday_master_prev:
                    NoticeBoard.objects.create(
                        user=data['user'],
                        notice=holiday.name,
                        holiday_id=holiday.id,
                        description=holiday.description,
                        start_date=holiday.start_date,
                        end_date=holiday.end_date,
                        published_datetime=holiday.start_date
                    )
                holiday_master_new = attendance.holiday_group.holiday. \
                    filter(
                        start_date__lte=data['buffer_date'], end_date__gte=data['today_date'])

                for holiday in holiday_master_new:
                    NoticeBoard.objects.update_or_create(
                        user=data['user'],
                        holiday_id=holiday.id,
                        defaults={
                            'notice': holiday.name,
                            'description': holiday.description,
                            'start_date': holiday.start_date,
                            'end_date': holiday.end_date,
                            'published_datetime': holiday.start_date,
                            'status': holiday.status
                        }
                    )

        except:
            pass

        # For birthday
        try:
            personal_obj = Personal.objects.get(employee=data['employee'])

            if data['today_date'].day == personal_obj.date_of_birth.day and \
                    data['today_date'].month == personal_obj.date_of_birth.month:
                NoticeBoard.objects.get_or_create(
                    user=data['user'],
                    start_date=data['today_date'],
                    end_date=data['today_date'],
                    notice='Happy Birthday!',
                    type='birthday',
                    defaults={
                        'published_datetime': datetime.now()
                    }

                )
        except:
            pass
    return


class AjaxMixin(object):
    def dispath(self, request, *args, **kwargs):
        if not request.is_ajax():
            raise Http404('This is an ajax request')

        return super().dispatch(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, AjaxMixin, View):
    _leave = None

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.dashboard == 'admin':
            return self.get_admin_dashboard()
        elif request.user.dashboard == 'management':
            return self.get_management_dashboard()
        elif request.user.dashboard == 'employee':
            return self.get_employee_dashboard()

    def get_employee_dashboard(self):
        data = {
            'approvals': self.get_approval(),
            'calendars': self.get_calendar(datetime.now()),
            'today_attendance': self.get_today_attendance(),
            'noticeboards': self.get_noticeboard(),
            'notifications': self.get_notification(),
            'attendance_statistics': self.get_attendance(datetime.now()),
            'leave_credit': self.get_leave_credit(),
            'yearly_status': self.get_yearly_status(),
        }

        return JsonResponse(data, status=200)

    def get_management_dashboard(self):
        """Dashboard data for Management."""

        data = {
            'approvals': self.get_approval(),
            'payment_disbursements': self.get_payment_disbursement_info(),
            'noticeboards': self.get_noticeboard(),
            'notifications': self.get_notification(),
            'calendars': self.get_calendar(datetime.now()),
            'employee_count': self.get_employee_count(),
            'salary_wise_breakdowns': self.get_salary_wise_breakdowns()
        }

        return JsonResponse(data, status=200)

    def get_admin_dashboard(self, attendance_date=None, attendance_month=None, attendance_year=None,
                            leave_date=None, leave_month=None, leave_year=None):
        """Dashboard data for Admin."""

        if not attendance_date:
            attendance_date = datetime.today().date()
        if not attendance_month:
            attendance_month = datetime.today().date().month
        if not attendance_year:
            attendance_year = datetime.today().date().year

        if not leave_date:
            leave_date = datetime.today().date()
        if not leave_month:
            leave_month = datetime.today().date().month
        if not leave_year:
            leave_year = datetime.today().date().year

        data = {
            'approvals': self.get_approval(),
            'noticeboards': self.get_noticeboard(),
            'notifications': self.get_notification(),
            'calendars': self.get_calendar(datetime.now()),
            'date_wise_attendance': self.get_date_wise_attendance(date=attendance_date),
            'month_wise_attendance': self.get_month_wise_attendance(month=attendance_month, year=attendance_year),
            'salary_wise_breakdowns': self.get_salary_wise_breakdowns(),
            'date_wise_leave': self.get_date_wise_leave(date=leave_date),
            'month_wise_leave': self.get_month_wise_leave(month=leave_month, year=leave_year),
            'year_wise_leave': self.get_year_wise_leave(year=leave_year),
        }

        return JsonResponse(data, status=200)

    def get_approval(self):
        """Get approval list for logged in user."""

        approvals = Approval(self.request).get(status_filtering='pending')
        approvals = map(map_for_approval, approvals)

        return list(approvals)

    def get_payment_disbursement_info(self):
        """Get payment disbursement info for every month."""

        return list(
            EmployeeSalary.objects.annotate(date=TruncMonth('end_date')).
            values('date').annotate(amount=Sum('net_earning')).
            order_by('amount')
        )

    def get_noticeboard(self):
        """ farzana & imam: Get notice for the user. """

        user = self.request.user
        employee = user.employee
        today_date = datetime.strptime("2020-03-16", "%Y-%m-%d")
        # today_date = datetime.now().date()
        buffer_date = today_date + timedelta(days=2)

        data = {
            'user': user,
            'employee': employee,
            'today_date': today_date,
            'buffer_date': buffer_date
        }
        set_noticeboard(data)

        noticeboard_qs = NoticeBoard.objects.filter(
            user=user, end_date__gte=today_date, start_date__lte=buffer_date, status=True
        ).order_by('-id')

        counter = noticeboard_qs.count()
        final_noticeboard = []
        for i in range(3):
            birthday_qs = noticeboard_qs.filter(type='birthday')
            if birthday_qs.exists() and birthday_qs[0].start_date == today_date:
                final_noticeboard.append(birthday_qs[0])
                noticeboard_qs = noticeboard_qs.exclude(id=birthday_qs[0].id)
            else:
                if noticeboard_qs.exists():
                    final_noticeboard.append(noticeboard_qs.first())
                    noticeboard_qs = noticeboard_qs.exclude(
                        id=noticeboard_qs.first().id)

        final_data = [{'counter': counter}]
        for my_notice in final_noticeboard:
            final_data.append({
                'notice': my_notice.notice,
                'description': my_notice.description,
                'start_date': my_notice.start_date,
                'end_date': my_notice.end_date,
                'published_datetime': my_notice.published_datetime
            })

        return final_data

    def get_notification(self):
        """Get notification late, leave, early out approval, decline list for Self."""

        notifications = Approval(self.request).get_notifications().values()

        return list(notifications)

    def get_calendar(self, date):
        """ farzana: Get personal calendar, mark for weekend and holiday """

        calendar = list()
        employee = self.request.user.employee

        schedule_record_qs = ScheduleRecord.objects.filter(date__month=date.month, date__year=date.year,
                                                           employee=employee)
        weekend_schedule = schedule_record_qs.filter(is_weekend=True)
        for weekend in weekend_schedule:
            calendar.append({
                'start_date': weekend.date,
                'end_date': weekend.date,
                'type': '',
                'name': 'Weekend'
            })

        # get holiday by date.month and date.year
        try:
            attendance = Attendance.objects.get(
                employee=employee).calendar_master
            if attendance and attendance.holiday_group:
                holiday_master = attendance.holiday_group.holiday
                for holiday in holiday_master.filter(status=True). \
                    filter(end_date__month__gte=date.month, start_date__month__lte=date.month,
                           end_date__year__gte=date.year, start_date__year__lte=date.year):
                    calendar.append({
                        'start_date': holiday.start_date,
                        'end_date': holiday.end_date,
                        'type': holiday.get_type_display(),
                        'name': holiday.name
                    })
        except Exception as e:
            print(e)

        return calendar

    def get_employee_count(self):
        """Get employee count based on gender."""

        employees = EmployeeIdentification.objects.all()
        male_employee = len(
            list(filter(lambda x: x.gender == 'male', employees)))
        female_employee = len(
            list(filter(lambda x: x.gender == 'female', employees)))
        other_employee = len(
            list(filter(lambda x: x.gender == 'other', employees)))

        return {
            'male': male_employee,
            'female_employee': female_employee,
            'other_employee': other_employee
        }

    def get_today_attendance(self):
        """ farzana: Get Today attendance """

        date = datetime.now()
        employee = self.request.user.employee

        try:
            in_time = AttendanceData.objects.get(
                employee=employee, date=date).in_time
            try:
                daily_record_obj = DailyRecord.objects.get(schedule_record__employee=employee,
                                                           schedule_record__date=date)
                is_present = daily_record_obj.is_present
                is_late = daily_record_obj.late
            except:
                is_present = ''
                is_late = ''

            today_attendance = {
                'in_time': in_time,
                'is_present': is_present,
                'is_late': is_late,
            }
        except:
            today_attendance = {}

        return today_attendance

    def get_attendance(self, date):
        """ farzana: Get month wise attendance """

        attendance_statistics = []
        attendance_data_qs = AttendanceData.objects.filter(employee=self.request.user.employee,
                                                           date__month=date.month, date__year=date.year)
        for attendance in attendance_data_qs:
            in_date = attendance.date
            in_time = attendance.in_time
            out_date = attendance.out_date
            out_time = attendance.out_time

            daily_record = ScheduleRecord.objects.get(employee=self.request.user.employee,
                                                      date=attendance.date).dailyrecord
            is_late = daily_record.late
            is_early = daily_record.early
            late_value = 0
            early_out_value = 0

            if is_late:
                late_value = daily_record.late_value

            if is_early:
                early_out_value = daily_record.early_out_value

            attendance_statistics.append({
                'in_date': in_date,
                'in_time': in_time,
                'out_time': out_time,
                'out_date': out_date,
                'is_late': is_late,
                'late_value': late_value,
                'early_out_value': early_out_value
            })

        return attendance_statistics

    def get_leave_credit(self):
        """ farzana: Get Leave credit for the employee """

        leave_list = []
        employee = self.request.user.employee
        try:
            leave_group = LeaveManage.objects.get(
                employee=employee).leave_group
            job = employee.employee_job_information.latest('updated_at')
            leave_remain_qs = LeaveRemaining.objects.filter(
                employee=employee, status=True, leave__status=True)

            for leave_remain in leave_remain_qs:
                credit = 0
                leave = leave_remain.leave
                try:
                    leave_settings = LeaveGroupSettings.objects.get(
                        leave_name=leave, leave_group=leave_group)
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
                    'leave_name': leave.name,
                    'credit': str(credit) + ' ' + leave.time_unit_basis,
                    'avail': (str(round(total_avail, 2)) if total_avail > 0 else str(0)) + ' ' + leave.time_unit_basis,
                    'remaining': (str(round(total_remain, 2)) if total_remain > 0 else str(
                        0)) + ' ' + leave.time_unit_basis,
                }

                leave_list.append(data)

        except:
            leave_list = leave_list

        return leave_list

    def get_yearly_status(self):
        """ farzana: Get count late, count early out, count under work of current year """

        counter_list = []
        dailyrecord_qs = DailyRecord.objects.filter(schedule_record__date__year=datetime.now().year,
                                                    schedule_record__employee=self.request.user.employee)

        for i in range(1, 13):
            month_wise_qs = dailyrecord_qs.filter(
                schedule_record__date__month=i)
            count_late = month_wise_qs.filter(late=True).count()
            count_early_out = month_wise_qs.filter(early=True).count()
            count_under_work = month_wise_qs.filter(under_work=True).count()

            counter_list.append({
                'month': i,
                'count_late': count_late,
                'count_early_out': count_early_out,
                'count_under_work': count_under_work,
            })

        return counter_list

    def get_date_wise_attendance(self, date=None):
        """ imam: Get attendance data date_wise """

        schedule_records = ScheduleRecord.objects.filter(date=date)
        total_present = len(
            list(filter(lambda record: record.dailyrecord.is_present, schedule_records)))
        late = len(
            list(filter(lambda record: record.dailyrecord.late, schedule_records)))
        present_on_time = total_present - late
        leave = len(list(filter(
            lambda record: record.is_leave and not record.dailyrecord.is_present, schedule_records
        )))
        absent = len(list(filter(
            lambda record: not record.is_leave and not record.dailyrecord.is_present and record.is_working_day,
            schedule_records
        )))
        data = {
            'present': present_on_time,
            'late': late,
            'leave': leave,
            'absent': absent
        }
        return data

    def get_month_wise_attendance(self, month, year):
        """ imam: Get attendance data for this month """

        schedule_records = ScheduleRecord.objects.filter(
            date__month=month, date__year=year).order_by('date')
        date_context = schedule_records.values('date').distinct()
        data = []
        for date_data in date_context:
            date_records = schedule_records.filter(date=date_data['date'])
            total_present = len(
                list(filter(lambda record: record.dailyrecord.is_present, date_records)))
            late = len(
                list(filter(lambda record: record.dailyrecord.late, date_records)))
            present_on_time = total_present - late
            leave = len(list(filter(
                lambda record: record.is_leave and not record.dailyrecord.is_present, date_records
            )))
            absent = len(list(filter(
                lambda record: not record.is_leave and not record.dailyrecord.is_present and record.is_working_day,
                date_records
            )))
            data.append({
                'date': str(date_data['date']),
                'present': present_on_time,
                'late': late,
                'leave': leave,
                'absent': absent
            })

        return data

    def get_salary_wise_breakdowns(self):
        """ imam: Get current employee salary wise breakdown """

        today = datetime.today().date()
        employee_salaries_qs = EmployeeVariableSalary.objects.filter(
            salary_structure__from_date__lte=today, salary_structure__to_date__gte=today, component__is_gross=True
        ).order_by('value')
        salary_list = []
        for salary in employee_salaries_qs:
            salary_list.append(salary.value)

        data = []
        if salary_list:
            max_salary = max(salary_list)
            min_salary = min(salary_list)
            slabs = 5
            range_value = math.ceil(
                (float(max_salary - min_salary) / slabs)/10000.0) * 10000
            salary_range_initiator = math.floor(
                float(min_salary)/10000.0) * 10000

            for slab in range(slabs):
                if slab == slabs - 1:
                    salary_range_finalizer = (
                        salary_range_initiator + range_value)
                else:
                    salary_range_finalizer = (
                        salary_range_initiator + range_value) - 1

                total_salaries = employee_salaries_qs.filter(
                    value__gte=salary_range_initiator, value__lte=salary_range_finalizer
                ).count()

                data.append({
                    'from': salary_range_initiator,
                    'to': salary_range_finalizer,
                    'total': total_salaries
                })
                salary_range_initiator = salary_range_finalizer + 1
        return data

    def get_date_wise_leave(self, date=None):
        """ imam: Get leave data date_wise """

        schedule_records_qs = ScheduleRecord.objects.filter(date=date)
        leaves_qs = LeaveMaster.objects.filter(status=True)
        leave_data = []
        for leave in leaves_qs:
            leave_data.append({
                'leave_type': leave.name,
                'availed': len(list(filter(
                    lambda record: record.dailyrecord.leave_master
                    and record.dailyrecord.leave_master.name == leave.name,
                    schedule_records_qs)))
            })
        data = {
            'date': date,
            'leaves': leave_data
        }

        return data

    def get_month_wise_leave(self, month=None, year=None):
        """ imam: Get leave data month_wise """

        schedule_records_qs = ScheduleRecord.objects.filter(
            date__month=month, date__year=year).order_by('date')
        date_context = schedule_records_qs.values('date').distinct()
        data = []
        leaves_qs = LeaveMaster.objects.filter(status=True)

        for date_data in date_context:
            date_records = schedule_records_qs.filter(date=date_data['date'])
            leaves_data = []
            for leave in leaves_qs:
                leaves_data.append({
                    'leave_type': leave.name,
                    'availed': len(list(filter(
                        lambda record: record.dailyrecord.leave_master
                        and record.dailyrecord.leave_master.name == leave.name,
                        date_records)))
                })
            data.append({
                'date': str(date_data['date']),
                'leaves': leaves_data
            })

        return data

    def get_year_wise_leave(self, year=None):
        """ imam: Get leave data year_wise """

        schedule_records_qs = ScheduleRecord.objects.filter(
            date__year=year).order_by('date')
        data = []
        leaves_qs = LeaveMaster.objects.filter(status=True)
        month = 1
        while month <= 12:
            month_records = schedule_records_qs.filter(date__month=month)
            if not month_records.exists():
                break
            leaves_data = []
            for leave in leaves_qs:
                self._leave = leave
                leaves_data.append({
                    'leave_type': leave.name,
                    'availed': len(
                        (list(filter(self.filter_record, month_records))))
                })
            data.append({
                'month': str(month),
                'leaves': leaves_data
            })
            month += 1

        return data

    def filter_record(self, record):
        if self._leave is not None:
            try:
                record.dailyrecord.leave_master.name
            except:
                pass
            else:
                if record.dailyrecord.leave_master.name == self._leave.name:
                    return record


class NoticeBoardListView(LoginRequiredMixin, PermissionMixin, ListView):
    """ farzana: ALl Notice List """

    template_name = 'dashboard/notice_board/list.html'
    model = NoticeBoard

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['permissions'] = self.get_current_user_permission_list()
        user = self.request.user
        employee = user.employee
        today_date = datetime.now().date()
        buffer_date = today_date + timedelta(days=2)

        data = {
            'user': user,
            'employee': employee,
            'today_date': today_date,
            'buffer_date': buffer_date
        }
        set_noticeboard(data)

        context['object_list'] = NoticeBoard.objects.filter(
            user=user).order_by('-published_datetime')

        return context

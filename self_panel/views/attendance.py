from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView
from datetime import datetime, date, timedelta
from django.utils import timezone
from employees.models import Attendance, LeaveManage
from helpers.mixins import PermissionMixin
from helpers.functions import get_organizational_structure
from attendance.models import *
from django.contrib import messages
from django.db import connection

from leave.models import LeaveEntry


def convert_time(t):
    parts = t.split(':')
    if len(parts[0]) == 1:
        parts[0] = '0{}'.format(parts[0])
        return ':'.join(parts)
    else:
        return t


def get_closest_to_dt(qs, dt):
    greater = qs.filter(work_start__gte=dt).order_by('work_start').first()
    less = qs.filter(work_start__lte=dt).order_by('-work_start').first()

    if greater and less:
        return greater if abs(
            datetime.strptime(str(greater.work_start), "%H:%M:%S") - datetime.strptime(str(dt), "%H:%M:%S")) < abs(
            datetime.strptime(str(less.work_start), "%H:%M:%S") - datetime.strptime(str(dt), "%H:%M:%S")) else less
    else:
        return greater or less


def get_late_day_status(em, in_d, in_t):
    is_present = True
    is_late = False
    late_value = 0
    daily_pre_overtime_seconds = 0
    in_t = datetime.strptime(in_t, '%H:%M').time() if type(in_t) is str else in_t
    late_application = LateApplication.objects.filter(attendance__date=in_d)
    if late_application.exists() is False:
        try:
            em_schedule = Attendance.objects.get(employee_id=em)
            em_deduction = LeaveManage.objects.filter(employee_id=em)
            late_component = ''
            if em_deduction:
                is_deduction = em_deduction[0].deduction
                if is_deduction:
                    late_component = em_deduction[0].deduction_group.late_component
            s_type = em_schedule.schedule_type
            timetable_record_qs = TimeTableRecord.objects.filter(schedule_record__employee=em,
                                                                 schedule_record__date=in_d)
            if timetable_record_qs:
                t_in_time = timetable_record_qs[0].in_time
                get_fraction_leave = LeaveEntry.objects.filter(employee_id=em, status='approved').filter(
                    Q(start_date__lte=in_d) & Q(end_date__gte=in_d)).filter(
                    Q(leave_type__partial_leave=True) | Q(leave_type__fractional=True))
                if get_fraction_leave:
                    if get_fraction_leave.last().start_time == t_in_time:
                        t_in_time = get_fraction_leave.last().end_time
                if s_type.schedule_type:
                    if in_t >= t_in_time:
                        late_value = (datetime.combine(date.today(), in_t) - datetime.combine(date.today(),
                                                                                              t_in_time)).seconds
                    else:
                        daily_pre_overtime_seconds = (
                            datetime.combine(date.today(), t_in_time) - datetime.combine(date.today(),
                                                                                         in_t)).seconds
                    if late_component not in ['', None]:
                        if late_component.latesetting.late_grace_time_unit == 'hour':
                            schedule_time = datetime.combine(date.today(), t_in_time) + timedelta(
                                hours=int(late_component.latesetting.late_grace_time))
                        else:
                            schedule_time = datetime.combine(date.today(), t_in_time) + timedelta(
                                minutes=int(late_component.latesetting.late_grace_time))
                        if in_t > schedule_time.time():
                            is_late = True

                        if late_component.latesetting.late_last_time_unit == 'hour':
                            last_time = datetime.combine(date.today(), t_in_time) + timedelta(
                                hours=int(late_component.latesetting.late_last_time))
                        else:
                            last_time = datetime.combine(date.today(), t_in_time) + timedelta(
                                minutes=int(late_component.latesetting.late_last_time))
                        if in_t > last_time.time():
                            is_present = False
        except:
            pass
    return is_late, late_value, is_present, daily_pre_overtime_seconds


def get_early_day_status(em, in_d, in_t, out_t, out_d):
    is_overtime = False
    daily_post_overtime_seconds = 0
    daily_work_seconds = 0
    is_early_out = False
    early_out_value = 0
    in_t = datetime.strptime(in_t, '%H:%M').time() if type(in_t) is str else in_t
    out_t = datetime.strptime(out_t, '%H:%M').time() if type(out_t) is str else out_t

    early_application = EarlyApplication.objects.filter(attendance__out_date=out_d)
    if early_application.exists() is False:
        # get daily working hour/seconds
        try:
            em_schedule = Attendance.objects.get(employee_id=em)
            em_deduction = LeaveManage.objects.filter(employee_id=em)
            early_out_component = ''
            if em_deduction:
                overtime = em_deduction[0].overtime
                if overtime:
                    is_overtime = True

                is_deduction = em_deduction[0].deduction
                if is_deduction:
                    early_out_component = em_deduction[0].deduction_group.early_out_component
            s_type = em_schedule.schedule_type
            timetable_record_qs = TimeTableRecord.objects.filter(schedule_record__employee=em,
                                                                 schedule_record__date=in_d)
            if timetable_record_qs:
                t_in_time = timetable_record_qs[0].in_time
                t_out_time = timetable_record_qs[0].out_time
                get_fraction_leave = LeaveEntry.objects.filter(employee_id=em, status='approved').filter(
                    Q(start_date__lte=in_d) & Q(end_date__gte=in_d)).filter(
                    Q(leave_type__partial_leave=True) | Q(leave_type__fractional=True))
                if get_fraction_leave:
                    if get_fraction_leave.last().start_time <= out_t:
                        t_out_time = in_t
                if s_type.schedule_type:
                    if t_out_time >= out_t:
                        early_out_value = (
                            datetime.combine(date.today(), t_out_time) - datetime.combine(date.today(),
                                                                                          out_t)).seconds
                        x_out_time = out_t
                    else:
                        # get overtime value
                        daily_post_overtime_seconds = (
                            datetime.combine(out_d, out_t) - datetime.combine(date.today(), t_out_time)).seconds
                        x_out_time = t_out_time

                    if t_in_time <= in_t:
                        daily_work_seconds = (
                            datetime.combine(out_d, x_out_time) - datetime.combine(in_d, in_t)).seconds
                    else:
                        daily_work_seconds = (
                            datetime.combine(out_d, x_out_time) - datetime.combine(in_d, t_in_time)).seconds

                    if early_out_component not in ['', None]:
                        if early_out_component.earlyoutsetting.early_out_allowed_time_unit == 'hour':
                            schedule_time = datetime.combine(date.today(), t_out_time) - timedelta(
                                hours=int(early_out_component.earlyoutsetting.early_out_allowed_time))
                        else:
                            schedule_time = datetime.combine(date.today(), t_out_time) - timedelta(
                                minutes=int(early_out_component.earlyoutsetting.early_out_allowed_time))
                        if schedule_time.time() > out_t:
                            is_early_out = True
        except:
            daily_work_seconds = (
                datetime.combine(out_d, out_t) - datetime.combine(in_d, in_t)).seconds
    return is_early_out, early_out_value, daily_work_seconds, is_overtime, daily_post_overtime_seconds


def get_under_work(em, work):
    is_under_work = False
    under_work_value = 0
    try:
        em_schedule = Attendance.objects.get(employee_id=em)
        s_type = em_schedule.schedule_type
        if s_type.total_working_hour_per_day_unit == 'hour':
            total_hour_per_day = int(s_type.total_working_hour_per_day) * 3600
        elif s_type.total_working_hour_per_day_unit == 'minute':
            total_hour_per_day = int(s_type.total_working_hour_per_day) * 60
        else:
            total_hour_per_day = 0
        if total_hour_per_day > work:
            is_under_work = True
            under_work_value = total_hour_per_day - work
    except:
        pass

    return is_under_work, under_work_value


class RemoteAttendanceView(LoginRequiredMixin, UserPassesTestMixin, PermissionMixin, TemplateView):
    """Ability to check in/out remotely."""

    # permission_required = []
    template_name = 'self_panel/attendance/remote_check_in.html'

    def test_func(self):
        return self.request.user.self_panel and self.request.user.employee

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['attendance_data'] = AttendanceData.objects.filter(employee=self.request.user.employee).last()

        return context

    def post(self, request, *args, **kwargs):
        context = dict()
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        current_datetime = datetime.now()
        check_time = current_datetime.time()
        check_date = current_datetime.date()
        employee = request.user.employee.id
        is_overtime = False
        is_early_out = False
        early_out_value = 0
        daily_work_seconds = 0
        daily_post_overtime_seconds = 0

        if 'check_in' in request.POST:
            if check_time not in ['', None]:
                in_time = check_time.strftime('%H:%M')
                is_late, late_value, is_present, daily_pre_overtime_seconds = \
                    get_late_day_status(employee, check_date, in_time)

                updated, created = AttendanceData.objects.update_or_create(employee_id=employee,
                                                                           date=check_date,
                                                                           defaults={'in_time': in_time})

                if updated:
                    record_update, record_create = DailyRecord.objects.update_or_create(
                        schedule_record__employee_id=employee,
                        schedule_record__date=check_date, defaults={'is_overtime': is_overtime,
                                                                    'daily_pre_overtime_seconds': daily_pre_overtime_seconds,
                                                                    'late': is_late, 'late_value': late_value,
                                                                    'is_present': is_present})

                    if record_update:
                        messages.success(request, 'Successfully checked in.')
        else:
            if check_time not in ['', None]:
                out_time = check_time.strftime('%H:%M')
                attendance_data = AttendanceData.objects.filter(employee=self.request.user.employee).last()
                if attendance_data:
                    in_date = attendance_data.date
                    in_time = attendance_data.in_time
                is_early_out, early_out_value, daily_work_seconds, is_overtime, daily_post_overtime_seconds = get_early_day_status(
                    employee, in_date, in_time, out_time, check_date)

                updated = AttendanceData.objects.filter(employee_id=employee, date=in_date).update(out_date=check_date,
                                                                                                   out_time=out_time)

                if updated:
                    is_under_work, under_work_value = get_under_work(employee, daily_work_seconds)
                    record_update, record_create = DailyRecord.objects.update_or_create(
                        schedule_record__employee_id=employee,
                        schedule_record__date=in_date, defaults={'daily_working_seconds': daily_work_seconds,
                                                                 'daily_post_overtime_seconds': daily_post_overtime_seconds,
                                                                 'early': is_early_out,
                                                                 'early_out_value': early_out_value,
                                                                 'under_work': is_under_work,
                                                                 'under_work_value': under_work_value})

                    if record_update:
                        messages.success(request, 'Successfully checked out.')

        return redirect(request, reverse('self_panel:remote_attendance'))


class AttendanceStatusView(LoginRequiredMixin, UserPassesTestMixin, PermissionMixin, ListView):
    """List of attendance status of the currently logged in employee."""

    template_name = 'self_panel/attendance/status.html'
    model = AttendanceData
    context_object_name = 'attendance_data'

    def test_func(self):
        return self.request.user.self_panel and self.request.user.employee

    def get_queryset(self):
        from_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        to_date = timezone.now().date()
        cursor = connection.cursor()

        if 'from_date' in self.request.GET:
            from_date = datetime.strptime(self.request.GET['from_date'], '%Y-%m-%d')

        if 'to_date' in self.request.GET:
            to_date = datetime.strptime(self.request.GET['to_date'], '%Y-%m-%d')

        cursor.execute('SELECT * FROM attendance_schedulerecord LEFT JOIN attendance_dailyrecord ON '
                       'attendance_schedulerecord.employee_id = attendance_dailyrecord.schedule_record_id '
                       'LEFT JOIN attendance_attendancedata ON '
                       'attendance_attendancedata.employee_id = attendance_schedulerecord.employee_id '
                       'and attendance_attendancedata.date = attendance_schedulerecord.date '
                       'WHERE attendance_schedulerecord.employee_id = ' + \
                       str(self.request.user.employee_id) + ' AND attendance_schedulerecord.date between "' + \
                       str(from_date) + '" and "' + str(to_date) + '"')

        return [
            dict(zip([col[0] for col in cursor.description], row))
            for row in cursor.fetchall()
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        return context

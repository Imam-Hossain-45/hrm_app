from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from attendance.forms import *
from attendance.models import *
from employees.models import Attendance, LeaveManage
from helpers.mixins import PermissionMixin
from datetime import timedelta, datetime, date
from django.shortcuts import render
from django.contrib import messages
from employees.models import EmployeeIdentification
from leave.models import LeaveEntry
from django.db.models import Q
from helpers.functions import get_organizational_structure, get_employee_query_info
from helpers import daily_record
from leave.forms import SearchForm


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
            timetable_record_qs = TimeTableRecord.objects.filter(schedule_record__employee=em, schedule_record__date=in_d)

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
        except Exception as e:
            print(e)

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
            timetable_record_qs = TimeTableRecord.objects.filter(schedule_record__employee=em, schedule_record__date=in_d)
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
    except Exception as e:
        print(e)

    return is_under_work, under_work_value


class ManualAttendanceList(LoginRequiredMixin, PermissionMixin, TemplateView):
    """
        show manual attendance
        Access: Super-Admin, Admin
        Url: /admin/attendance/process/manual_entry/
    """
    template_name = 'attendance/process/manual_attendance/list.html'
    permission_required = ['add_attendancedata', 'change_attendancedata', 'view_attendancedata',
                           'delete_attendancedata']

    def get_day_status(self, em, date):
        try:
            daily_record = DailyRecord.objects.get(schedule_record__employee=em, schedule_record__date=date)
            if daily_record.late:
                temp_status = 'Late'
            elif daily_record.schedule_record.is_holiday:
                temp_status = 'Holiday'
            elif daily_record.schedule_record.is_weekend:
                temp_status = 'Weekend'
            else:
                temp_status = 'On Time'
            if daily_record.early:
                temp_status = str(temp_status) + ' - ' + 'Early Out'

            if daily_record.schedule_record.is_leave:
                if daily_record.is_present:
                    temp_status = str(temp_status) + ' (' + daily_record.leave_master.short_name + ')'
                else:
                    temp_status = daily_record.leave_master.short_name

            if daily_record.schedule_record.is_working_day and daily_record.schedule_record.is_leave is False \
                    and daily_record.is_present is False:
                temp_status = 'Absent'
            status_dict = {'id': em.id, 'date': date, 'd_status': temp_status}
            return status_dict
        except:
            return False

    def get_instance(self):
        employee = ''
        if self.request.GET.get('query'):
            employee = self.request.GET.get('employee')
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')
        company = self.request.GET.get('company')
        division = self.request.GET.get('division')
        department = self.request.GET.get('department')
        business_unit = self.request.GET.get('business_unit')
        branch = self.request.GET.get('branch')
        schedule = self.request.GET.get('schedule')
        loop_times = ''
        attendance_list = ''
        has_attendance = []
        em_leave_status = []
        if from_date in ['', None]:
            data = AttendanceData.objects.order_by('date').first()
            if data:
                from_date = str(data.date)
            else:
                from_date = datetime.today().date()

        if to_date in ['', None]:
            to_date = datetime.today().date()

        if from_date not in ['', None] and to_date not in ['', None]:
            d = datetime.strptime(str(to_date), '%Y-%m-%d') - datetime.strptime(str(from_date), '%Y-%m-%d')
            day = []
            for i in range(d.days + 1):
                temp = datetime.strptime(str(from_date), '%Y-%m-%d') + timedelta(days=i)
                day.append(temp.date())
            loop_times = day

        # search by various category
        if employee not in ['', None] or from_date not in ['', None] or\
            to_date not in ['', None] or company not in ['', None] or \
            division not in ['', None] or department not in ['', None] or \
                business_unit not in ['', None] or branch not in ['', None] or schedule not in ['', None]:
            object_list = EmployeeIdentification.objects
            if employee not in ['', None]:
                object_list = object_list.filter(id=employee)
            if company not in ['', None]:
                object_list = object_list.filter(employee_job_informations__company=company)
            if division not in ['', None]:
                object_list = object_list.filter(employee_job_informations__division=division)
            if department not in ['', None]:
                object_list = object_list.filter(employee_job_informations__department=department)
            if business_unit not in ['', None]:
                object_list = object_list.filter(employee_job_informations__business_unit=business_unit)
            if schedule not in ['', None]:
                object_list = object_list.filter(employee_attendance__schedule_type=schedule)
            object_list = object_list.order_by('created_at')

            if from_date not in ['', None] and to_date not in ['', None]:
                attendace_item = []
                has_daily_attendance = ''
                for obj in object_list:
                    for i in loop_times:
                        em_leave_status.append(self.get_day_status(obj, i))

                        daily_attendance = AttendanceData.objects.filter(employee=obj, date=i)
                        if daily_attendance:
                            daily_attendance = daily_attendance.latest('created_at')
                            has_daily_attendance = daily_attendance.employee.id
                            attendace_dict = {
                                'id': daily_attendance.employee.id,
                                'attendance_id': daily_attendance.id,
                                'date': daily_attendance.date,
                                'in_time': daily_attendance.in_time,
                                'out_time': daily_attendance.out_time,
                                'out_date': daily_attendance.out_date,
                            }
                            daily_break = AttendanceBreak.objects.filter(
                                attendance_id=daily_attendance.id)
                            break_item = []
                            for b in daily_break:
                                break_dict = {
                                    'id': b.id,
                                    'break_start': b.break_start,
                                    'break_start_date': b.break_start_date,
                                    'break_end': b.break_end,
                                    'break_end_date': b.break_end_date,
                                }
                                break_item.append(break_dict)
                            attendace_dict['break_data'] = break_item
                            attendace_item.append(attendace_dict)
                        attendance_list = attendace_item

                    has_attendance.append(has_daily_attendance)
        else:
            object_list = EmployeeIdentification.objects.all().order_by('created_at')

        return loop_times, object_list, attendance_list, has_attendance, em_leave_status

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = ''
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['attendance_form'] = AttendanceForm()
        context['action_attendance_form'] = ActionAttendanceForm()
        context['attendance_break_form'] = AttendanceBreakForm()

        search_form = SearchForm()
        if 'attendance_search' in self.request.GET:
            search_form = SearchForm(self.request.GET)
            from_date = self.request.GET.get('from_date')
            to_date = self.request.GET.get('to_date')

            if from_date in EMPTY_VALUES:
                search_form.add_error('from_date', 'This field is required')

            if to_date in EMPTY_VALUES:
                search_form.add_error('to_date', 'This field is required')

            if search_form.is_valid():
                loop_times, object_list, attendance_list, has_attendance, em_leave_status = self.get_instance()
                if loop_times is not '':
                    context['loop_times'] = loop_times
                if object_list is not '':
                    context['object_list'] = object_list
                if attendance_list is not '':
                    context['attendance_list'] = attendance_list
                if has_attendance is not '':
                    context['has_attendance'] = has_attendance
                if em_leave_status is not '':
                    context['em_leave_status'] = em_leave_status

            if self.request.GET.get('query'):
                employee = self.request.GET.get('employee')

            if employee:
                context['employee'] = get_employee_query_info(employee)

        context['search_form'] = search_form

        # paginator = Paginator(loop_times, 2)  # Show 25 contacts per page
        # page = self.request.GET.get('page')
        # context['loop_times'] = paginator.get_page(page)

        return context

    def post(self, request, *args, **kwargs):
        context = dict()
        employee = ''
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['search_form'] = SearchForm()
        context['action_attendance_form'] = ActionAttendanceForm()
        attendance_break_form = AttendanceBreakForm(request.POST or None)
        context['attendance_form'] = AttendanceForm()
        context['attendance_break_form'] = attendance_break_form

        if self.request.GET.get('query'):
            employee = self.request.GET.get('employee')

        if employee:
            context['employee'] = get_employee_query_info(employee)

        if 'form1' in request.POST:
            post_dict = self.request.POST.copy()
            post_dict['date'] = datetime.strptime(request.POST['date'], '%d/%m/%Y')
            if self.request.POST.get('in_time') not in ['', None]:
                post_dict['in_time'] = datetime.strptime(convert_time(self.request.POST['in_time']),
                                                         '%I:%M %p')
                post_dict['in_time'] = post_dict['in_time'].strftime('%H:%M')
            if self.request.POST.get('out_time') not in ['', None]:
                post_dict['out_time'] = datetime.strptime(convert_time(self.request.POST['out_time']),
                                                          '%I:%M %p')
                post_dict['out_time'] = post_dict['out_time'].strftime('%H:%M')

            attendance_form = AttendanceForm(post_dict)
            context['attendance_form'] = attendance_form

            print(attendance_form.errors)
            if attendance_form.is_valid() and attendance_break_form.is_valid():
                # delete attendance break
                if request.POST.get('del_break') not in ['', None]:
                    del_break = request.POST['del_break'].split(',')
                    for d in del_break:
                        AttendanceBreak.objects.filter(id=d).delete()

                for i, in_time in enumerate(request.POST.getlist('in_time')):
                    if in_time not in ['', None]:
                        is_overtime = False
                        is_early_out = False
                        early_out_value = 0
                        daily_work_seconds = 0
                        daily_post_overtime_seconds = 0
                        in_time = datetime.strptime(convert_time(request.POST.getlist('in_time')[i]),
                                                    '%I:%M %p')
                        in_time = in_time.strftime('%H:%M')

                        """Save data in ScheduleRecord and DailyRecord"""
                        daily_record_data = {
                            'employee': request.POST.getlist('employee')[i],
                            'date': datetime.strptime(str(request.POST.getlist('date')[i]), '%d/%m/%Y').date()
                        }

                        daily_record.set_daily_record(daily_record_data)

                        """ get late or not """
                        is_late, late_value, is_present, daily_pre_overtime_seconds = \
                            get_late_day_status(request.POST.getlist('employee')[i], datetime.strptime(
                                request.POST.getlist('date')[i],
                                '%d/%m/%Y'), in_time)

                        if request.POST.getlist('out_time')[i] not in ['', None]:
                            out_time = datetime.strptime(convert_time(request.POST.getlist('out_time')[i]),
                                                         '%I:%M %p')
                            out_time = out_time.strftime('%H:%M')

                            out_date = datetime.strptime(request.POST.getlist('out_date')[i], '%Y-%m-%d')

                            if out_date not in ['', None]:
                                out_date = out_date
                            else:
                                out_date = datetime.strptime(request.POST.getlist('date')[i], '%d/%m/%Y')

                            is_early_out, early_out_value, daily_work_seconds, is_overtime, daily_post_overtime_seconds = get_early_day_status(
                                request.POST.getlist('employee')[i],
                                datetime.strptime(
                                    request.POST.getlist('date')[i],
                                    '%d/%m/%Y'), in_time, out_time, out_date)
                        else:
                            out_time = None
                            out_date = None

                        if request.POST.getlist('attendance_id')[i] not in ['', None]:
                            AttendanceData.objects.filter(
                                id=request.POST.getlist('attendance_id')[i],
                                employee_id=request.POST.getlist('employee')[i],
                                date=datetime.strptime(
                                    request.POST.getlist('date')[i],
                                    '%d/%m/%Y')).update(
                                in_time=in_time, out_time=out_time,
                                out_date=out_date)
                            pk = request.POST.getlist('attendance_id')[i]
                        else:
                            updated = AttendanceData.objects.create(employee_id=request.POST.getlist('employee')[i],
                                                                    date=datetime.strptime(
                                                                        request.POST.getlist('date')[i],
                                                                        '%d/%m/%Y'), in_time=in_time, out_time=out_time,
                                                                    out_date=out_date)
                            pk = updated.pk

                        prefix_name = request.POST.getlist('employee')[i] + '_' + str(
                            datetime.strptime(request.POST.getlist('date')[i], '%d/%m/%Y').date())
                        daily_break_seconds = 0

                        for j, break_start in enumerate(request.POST.getlist(prefix_name + '_break_start')):
                            if break_start not in ['', None]:
                                break_start = datetime.strptime(
                                    convert_time(request.POST.getlist(prefix_name + '_break_start')[j]), '%I:%M %p')
                                break_start = break_start.strftime('%H:%M')

                                break_start_date = request.POST.getlist(prefix_name + '_break_start_date')[j]
                                if break_start_date.strip() not in EMPTY_VALUES:
                                    break_start_date = datetime.strptime(break_start_date, '%Y-%m-%d')
                                else:
                                    break_start_date = datetime.strptime(request.POST.getlist('date')[i], '%d/%m/%Y')

                                if request.POST.getlist(prefix_name + '_break_end')[j] not in ['', None]:
                                    break_end = datetime.strptime(
                                        convert_time(request.POST.getlist(prefix_name + '_break_end')[j]), '%I:%M %p')
                                    break_end = break_end.strftime('%H:%M')

                                    break_end_date = request.POST.getlist(prefix_name + '_break_end_date')[j]
                                    if break_end_date.strip() not in EMPTY_VALUES:
                                        break_end_date = datetime.strptime(
                                            request.POST.getlist(prefix_name + '_break_end_date')[j], '%Y-%m-%d')
                                    else:
                                        break_end_date = datetime.strptime(request.POST.getlist('date')[i],
                                                                           '%d/%m/%Y')
                                    # get daily break hour/seconds
                                    daily_break_seconds = daily_break_seconds + (datetime.combine(break_end_date,
                                                                                                  datetime.strptime(
                                                                                                      break_end,
                                                                                                      '%H:%M').time()) - datetime.combine(
                                        break_start_date, datetime.strptime(break_start, '%H:%M').time())).seconds
                                else:
                                    break_end = None
                                    break_end_date = None

                                if request.POST.getlist(prefix_name + '_break_id')[j] not in ['', None]:
                                    AttendanceBreak.objects.filter(
                                        id=request.POST.getlist(prefix_name + '_break_id')[j]).update(
                                        attendance_id=pk, break_start=break_start,
                                        break_start_date=break_start_date,
                                        break_end=break_end, break_end_date=break_end_date)
                                else:
                                    AttendanceBreak.objects.create(attendance_id=pk, break_start=break_start,
                                                                   break_start_date=break_start_date,
                                                                   break_end=break_end, break_end_date=break_end_date)

                        daily_work_seconds = daily_work_seconds - daily_break_seconds
                        is_under_work, under_work_value = get_under_work(request.POST.getlist('employee')[i],
                                                                         daily_work_seconds)

                        """ Update dailyRecord """
                        DailyRecord.objects.filter(
                            schedule_record__employee_id=request.POST.getlist('employee')[i],
                            schedule_record__date=datetime.strptime(
                                                       request.POST.getlist('date')[i], '%d/%m/%Y')).update(
                            daily_working_seconds=daily_work_seconds, is_overtime=is_overtime,
                            daily_pre_overtime_seconds=daily_pre_overtime_seconds,
                            daily_post_overtime_seconds=daily_post_overtime_seconds, late=is_late,
                            late_value=late_value,
                            early=is_early_out, early_out_value=early_out_value, under_work=is_under_work,
                            under_work_value=under_work_value, is_present=is_present)

                messages.success(request, 'Successfully Saved.')
        else:
            is_early_out = False
            early_out_value = 0
            daily_work_seconds = 0
            is_overtime = False
            daily_post_overtime_seconds = 0
            is_late = False
            late_value = 0
            is_present = True
            daily_pre_overtime_seconds = 0
            post_dict = self.request.POST.copy()

            if self.request.POST.get('in_time') not in ['', None]:
                post_dict['in_time'] = datetime.strptime(convert_time(self.request.POST['in_time']),
                                                         '%I:%M %p')
                post_dict['in_time'] = post_dict['in_time'].strftime('%H:%M')
            if self.request.POST.get('out_time') not in ['', None]:
                post_dict['out_time'] = datetime.strptime(convert_time(self.request.POST['out_time']),
                                                          '%I:%M %p')
                post_dict['out_time'] = post_dict['out_time'].strftime('%H:%M')

            context['action_attendance_form'] = ActionAttendanceForm(post_dict)
            action_attendance_form = context['action_attendance_form']
            print(action_attendance_form.errors)

            if action_attendance_form.is_valid() and attendance_break_form.is_valid():

                loop_times, object_list, attendance_list, has_attendance, em_leave_status = self.get_instance()
                for i in loop_times:
                    if action_attendance_form.cleaned_data.get('in_date') not in ['', None]:
                        in_date = action_attendance_form.cleaned_data.get('in_date')
                    else:
                        in_date = i
                    if action_attendance_form.cleaned_data.get('out_date') not in ['', None]:
                        out_date = action_attendance_form.cleaned_data.get('out_date')
                    else:
                        out_date = i

                    for obj in object_list:
                        attendance = AttendanceData.objects.create(
                            employee=obj,
                            date=in_date,
                            in_time=action_attendance_form.cleaned_data.get('in_time'),
                            out_time=action_attendance_form.cleaned_data.get('out_time'),
                            out_date=out_date,
                        )

                        if attendance.in_time not in EMPTY_VALUES:
                            """Save data in ScheduleRecord and DailyRecord"""
                            daily_record_data = {
                                'employee': obj.id,
                                'date': attendance.date
                            }

                            daily_record.set_daily_record(daily_record_data)

                            """ get late or not """
                            is_late, late_value, is_present, daily_pre_overtime_seconds = \
                                get_late_day_status(obj.id, attendance.date, attendance.in_time.strftime('%H:%M'))

                        if attendance.in_time not in EMPTY_VALUES and attendance.out_time not in EMPTY_VALUES:
                            is_early_out, early_out_value, daily_work_seconds, is_overtime, daily_post_overtime_seconds = get_early_day_status(
                                obj.id, attendance.date, attendance.in_time.strftime('%H:%M'),
                                attendance.out_time.strftime('%H:%M'),
                                attendance.out_date)

                        daily_break_seconds = 0
                        for j, break_start in enumerate(request.POST.getlist('__break_start')):
                            if break_start not in ['', None]:
                                break_start = datetime.strptime(
                                    convert_time(request.POST.getlist('__break_start')[j]),
                                    '%I:%M %p')
                                break_start = break_start.strftime('%H:%M')

                                break_start_date = request.POST.getlist('__break_start_date')[j]
                                if break_start_date not in ['', None]:
                                    break_start_date = break_start_date
                                else:
                                    break_start_date = in_date

                                if request.POST.getlist('__break_end')[j] not in ['', None]:
                                    break_end = datetime.strptime(
                                        convert_time(request.POST.getlist('__break_end')[j]),
                                        '%I:%M %p')
                                    break_end = break_end.strftime('%H:%M')

                                    break_end_date = request.POST.getlist('__break_end_date')[j]
                                    if break_end_date not in ['', None]:
                                        break_end_date = break_end_date
                                    else:
                                        break_end_date = in_date
                                    # get daily break hour/seconds
                                    daily_break_seconds = daily_break_seconds + (
                                        datetime.combine(break_end_date,
                                                         datetime.strptime(break_end, '%H:%M').time()) -
                                        datetime.combine(break_start_date,
                                                         datetime.strptime(break_start, '%H:%M').time())).seconds

                                else:
                                    break_end = None
                                    break_end_date = None
                                AttendanceBreak.objects.create(attendance_id=attendance.pk,
                                                               break_start=break_start,
                                                               break_start_date=break_start_date,
                                                               break_end=break_end,
                                                               break_end_date=break_end_date)
                        daily_work_seconds = daily_work_seconds - daily_break_seconds
                        is_under_work, under_work_value = get_under_work(obj.id, daily_work_seconds)

                        """ Update dailyRecord """
                        DailyRecord.objects.filter(
                            schedule_record__employee_id=obj.id,
                            schedule_record__date=attendance.date).update(
                            daily_working_seconds=daily_work_seconds, is_overtime=is_overtime,
                            daily_pre_overtime_seconds=daily_pre_overtime_seconds,
                            daily_post_overtime_seconds=daily_post_overtime_seconds, late=is_late,
                            late_value=late_value,
                            early=is_early_out, early_out_value=early_out_value, under_work=is_under_work,
                            under_work_value=under_work_value, is_present=is_present)

                messages.success(request, 'Successfully Saved.')
            else:
                # both action form invalid and no data saved.
                messages.error(request, 'No data saved.')

        loop_times, object_list, attendance_list, has_attendance, em_leave_status = self.get_instance()
        if loop_times is not '':
            context['loop_times'] = loop_times
        if object_list is not '':
            context['object_list'] = object_list
        if attendance_list is not '':
            context['attendance_list'] = attendance_list
        if has_attendance is not '':
            context['has_attendance'] = has_attendance
        if em_leave_status is not '':
            context['em_leave_status'] = em_leave_status

        return render(request, self.template_name, context)

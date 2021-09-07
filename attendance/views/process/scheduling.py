from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.views.generic import TemplateView

from helpers import daily_record
from helpers.mixins import PermissionMixin
from attendance.forms import ActionSchedulingForm, SchedulingForm, SchedulingBreakForm, SchedulingTimetableForm
from attendance.models import ScheduleRecord, TimeTableRecord, BreakTimeRecord, EmployeeIdentification
from datetime import datetime, timedelta
from django.shortcuts import render
from django.contrib import messages
from helpers.functions import get_organizational_structure, get_employee_query_info
from leave.forms import SearchForm
from django.core.validators import EMPTY_VALUES


def convert_time(t):
    parts = t.split(':')
    if len(parts[0]) == 1:
        parts[0] = '0{}'.format(parts[0])
        return ':'.join(parts)
    else:
        return t


class SchedulerRecordView(LoginRequiredMixin, PermissionMixin, TemplateView):
    template_name = 'attendance/process/scheduling/list.html'
    form_class = SchedulingForm
    second_form_class = SchedulingTimetableForm
    third_form_class = SchedulingBreakForm
    fourth_form_class = ActionSchedulingForm
    fifth_form_class = SearchForm
    permission_required = ['add_schedulerecord', 'change_schedulerecord', 'view_schedulerecord',
                           'delete_schedulerecord']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = ''
        object_list = None
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['scheduling_form'] = self.form_class
        context['scheduling_time_form'] = self.second_form_class
        context['scheduling_break_form'] = self.third_form_class
        context['action_scheduling_form'] = self.fourth_form_class

        search_form = self.fifth_form_class()
        if 'scheduling-search' in self.request.GET:
            search_form = self.fifth_form_class(self.request.GET)
            from_date = self.request.GET.get('from_date')
            to_date = self.request.GET.get('to_date')

            if from_date in EMPTY_VALUES:
                search_form.add_error('from_date', 'This field is required')

            if to_date in EMPTY_VALUES:
                search_form.add_error('to_date', 'This field is required')

            if search_form.is_valid():
                scheduling_list = self.get_instance()
                if scheduling_list is not '':
                    object_list = scheduling_list
                else:
                    context['no_schedule'] = 'No scheduling found.'

                if self.request.GET.get('query'):
                    if scheduling_list is not '':
                        object_list = scheduling_list
                    else:
                        context['no_schedule'] = 'No scheduling found.'

                if object_list:
                    paginator = Paginator(object_list, 50)
                    page = self.request.GET.get('page')
                    context['scheduling_list'] = paginator.get_page(page)
                    index = context['scheduling_list'].number - 1
                    max_index = len(paginator.page_range)
                    start_index = index - 0 if index >= 3 else 0
                    end_index = index + 5 if index <= max_index - 5 else max_index
                    context['page_range'] = list(paginator.page_range)[start_index:end_index]
                    context['path'] = "%s" % "&".join(
                        ["%s=%s" % (key, value) for (key, value) in self.request.GET.items()
                         if not key == 'page'])

            if self.request.GET.get('query'):
                employee = self.request.GET.get('employee')

            if employee:
                context['employee'] = get_employee_query_info(employee)

        context['search_form'] = search_form

        return context

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
        schedule_list = []
        loop_times = ''

        if from_date in ['', None]:
            data = ScheduleRecord.objects.order_by('date').first()
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
        if employee not in ['', None] or from_date not in ['', None] \
            or to_date not in ['', None] or company not in ['', None] \
            or division not in ['', None] or department not in ['', None] \
            or business_unit not in ['', None] or branch not in ['', None] \
                or schedule not in ['', None]:

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
                for obj in object_list:
                    """Save data in ScheduleRecord and DailyRecord"""
                    daily_record_data = {
                        'employee': obj.id,
                        'date': datetime.strptime(str(to_date), '%Y-%m-%d').date()
                    }

                    try:
                        daily_record.set_daily_record(daily_record_data)
                    except Exception as e:
                        print(e)
                        messages.add_message(self.request, messages.ERROR,
                                             ("There is no date of joining for " + str(obj) + " ."))

                    for i in loop_times:
                        schedule_record = ScheduleRecord.objects.filter(employee=obj, date=i)
                        if schedule_record.exists():
                            if schedule_record[0].is_holiday:
                                schedule_status = 'Holiday'
                            elif schedule_record[0].is_weekend:
                                schedule_status = 'Weekend'
                            elif schedule_record[0].is_leave:
                                schedule_status = 'Leave'
                            else:
                                schedule_status = '-'
                            schedule_dict = {
                                'id': obj.id,
                                'name': obj,
                                'designation': obj.employee_job_information.last().designation if obj.employee_job_information.last() is not None else None,
                                'employee_id': obj.employee_id,
                                'schedule_type': obj.employee_attendance.last().schedule_type.get_schedule_type_display() if obj.employee_attendance.last().schedule_type is not None else None,
                                'roster_type': obj.employee_attendance.last().schedule_type.get_roster_type_display() if obj.employee_attendance.last().schedule_type is not None else None,
                                'date': i,
                                'in_time': schedule_record[0].timetable_record_model.in_time,
                                'out_time': schedule_record[0].timetable_record_model.out_time,
                                'out_date': schedule_record[0].timetable_record_model.out_date,
                                'status': schedule_status,
                                'work_day': schedule_record[0].is_working_day,
                                'schedule_record_id': schedule_record[0].id
                            }
                            daily_break = BreakTimeRecord.objects.filter(
                                timetable_record=schedule_record[0].timetable_record_model)
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
                            schedule_dict['break_data'] = break_item
                            schedule_list.append(schedule_dict)

        return schedule_list

    def check_out_time(self, in_date, in_time, out_date, out_time):
        if in_date not in ['', None] and in_time not in ['', None] and out_date not in ['', None] \
                and out_time not in ['', None]:
            in_datetime = str(in_date) + ' ' + str(in_time)
            out_datetime = str(out_date) + ' ' + str(out_time)
            if datetime.strptime(in_datetime, '%Y-%m-%d %H:%M') > datetime.strptime(out_datetime, '%Y-%m-%d %H:%M'):
                return True
            else:
                return False

    def post(self, request):
        context = dict()
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['search_form'] = self.fifth_form_class()
        scheduling_form = self.form_class()
        context['scheduling_form'] = scheduling_form
        action_scheduling_form = self.fourth_form_class
        context['action_scheduling_form'] = action_scheduling_form
        scheduling_time_form = self.second_form_class
        context['scheduling_time_form'] = scheduling_time_form
        scheduling_break_form = self.third_form_class(request.POST or None)
        context['scheduling_break_form'] = scheduling_break_form
        scheduling_list = self.get_instance()
        employee = self.request.GET.get('employee')

        if scheduling_list:
            paginator = Paginator(scheduling_list, 50)
            page = self.request.GET.get('page')
            scheduling_list = paginator.get_page(page)

        if self.request.GET.get('employee'):
            context['employee'] = get_employee_query_info(employee)

        if request.POST:
            post_dict = self.request.POST.copy()
            if self.request.POST.get('in_time') not in ['', None]:
                post_dict['in_time'] = datetime.strptime(convert_time(self.request.POST['in_time']),
                                                         '%I:%M %p')
                post_dict['in_time'] = post_dict['in_time'].strftime('%H:%M')
            if self.request.POST.get('out_time') not in ['', None]:
                post_dict['out_time'] = datetime.strptime(convert_time(self.request.POST['out_time']),
                                                          '%I:%M %p')
                post_dict['out_time'] = post_dict['out_time'].strftime('%H:%M')

            if 'form1' in request.POST:
                scheduling_time_form = self.second_form_class(request.POST)
                context['scheduling_time_form'] = scheduling_time_form

                if scheduling_time_form.is_valid() and scheduling_break_form.is_valid():
                    for s in scheduling_list:
                        in_time = request.POST.get('in_time_' + str(s['id']) + str('_') + str(s['date']), False)

                        if in_time or in_time in ['', None]:
                            if in_time not in ['', None]:
                                in_time = datetime.strptime(convert_time(in_time),
                                                            '%I:%M %p')
                                in_time = in_time.strftime('%H:%M')
                            else:
                                in_time = None

                            out_time = request.POST['out_time_' + str(s['id']) + str('_') + str(s['date'])]
                            if out_time not in ['', None]:
                                out_time = datetime.strptime(
                                    convert_time(request.POST['out_time_' + str(s['id']) + str('_') + str(s['date'])]),
                                    '%I:%M %p')
                                out_time = out_time.strftime('%H:%M')
                            else:
                                out_time = None

                            work_day = request.POST.get('is_working_day_' + str(s['id']) + str('_') + str(s['date']))
                            if work_day == 'not_work_day':
                                is_working_day = False
                            else:
                                is_working_day = True

                            out_date = request.POST['out_date_' + str(s['id']) + str('_') + str(s['date'])]
                            if out_date not in ['', None]:
                                out_date = out_date
                            else:
                                out_date = s['date']

                            # check in time or date not greater than out time or date
                            if self.check_out_time(s['date'], in_time, out_date, out_time):
                                messages.error(request, "Out date or time should be greater than in time or date.")
                                # scheduling_list = self.get_instance()
                                context['scheduling_list'] = scheduling_list
                                return render(request, self.template_name, context)

                            schedule_record_qs = ScheduleRecord.objects.filter(date=s['date'], employee=s['id'])
                            schedule_record_qs.update(
                                is_working_day=is_working_day,
                                is_weekend=False if is_working_day is True else schedule_record_qs[0].is_weekend,
                                is_holiday=False if is_working_day is True else schedule_record_qs[0].is_holiday
                            )

                            time_record_qs = TimeTableRecord.objects.filter(schedule_record__date=s['date'],
                                                                            schedule_record__employee=s['id'])
                            time_record_qs.update(in_time=in_time, out_date=out_date, out_time=out_time)

                            # break time record
                            break_start_temp = request.POST.getlist(
                                str(s['id']) + str('_') + str(s['date']) + '_break_start')
                            break_start_date_temp = request.POST.getlist(
                                str(s['id']) + str('_') + str(s['date']) + '_break_start_date')
                            break_end_temp = request.POST.getlist(str(s['id']) + str('_') + str(s['date']) + '_break_end')
                            break_end_date_temp = request.POST.getlist(
                                str(s['id']) + str('_') + str(s['date']) + '_break_end_date')

                            break_time_qs = BreakTimeRecord.objects
                            break_time_qs.filter(timetable_record_id=time_record_qs[0].id).delete()
                            for j, start_time in enumerate(break_start_temp):
                                if start_time not in ['', None]:
                                    break_start = datetime.strptime(convert_time(start_time), '%I:%M %p')
                                    break_start = break_start.strftime('%H:%M')
                                    if break_start_date_temp[j] not in ['', None]:
                                        break_start_date = break_start_date_temp[j]
                                    else:
                                        break_start_date = s['date']

                                    # check break start time or date not greater than out time or date
                                    if self.check_out_time(break_start_date, break_start, out_date, out_time):
                                        messages.error(request,
                                                       "Break start date or time should not "
                                                       "be greater than end time or date.")
                                        # scheduling_list = self.get_instance()
                                        context['scheduling_list'] = scheduling_list
                                        return render(request, self.template_name, context)

                                    # check break start time or date not greater than in time or date
                                    if self.check_out_time(s['date'], in_time, break_start_date, break_start):
                                        messages.error(request,
                                                       "Break start date or time should be "
                                                       "greater than in time or date.")
                                        # scheduling_list = self.get_instance()
                                        context['scheduling_list'] = scheduling_list
                                        return render(request, self.template_name, context)

                                    break_end_date = s['date']
                                    if break_end_temp[j] not in ['', None]:
                                        break_end = datetime.strptime(convert_time(break_end_temp[j]), '%I:%M %p')
                                        break_end = break_end.strftime('%H:%M')
                                        if break_end_date_temp[j] not in ['', None]:
                                            break_end_date = break_end_date_temp[j]
                                    else:
                                        break_end = None

                                    # check break end time or date not greater than out time or date
                                    if self.check_out_time(break_end_date, break_end, out_date, out_time):
                                        messages.error(request,
                                                       "Break start date or time should not "
                                                       "be greater than end time or date.")
                                        # scheduling_list = self.get_instance()
                                        context['scheduling_list'] = scheduling_list
                                        return render(request, self.template_name, context)

                                    # check break start time or date not greater than break end time or date
                                    if self.check_out_time(break_start_date, break_start, break_end_date, break_end):
                                        messages.error(request,
                                                       "Break end date or time should be greater "
                                                       "than break start time or date.")
                                        # scheduling_list = self.get_instance()
                                        context['scheduling_list'] = scheduling_list
                                        return render(request, self.template_name, context)
                                    break_time_qs.create(timetable_record_id=time_record_qs[0].id,
                                                         break_start=break_start,
                                                         break_start_date=break_start_date,
                                                         break_end=break_end,
                                                         break_end_date=break_end_date)
                    messages.success(request, 'Successfully Saved.')
            else:
                schedule_record_id = request.POST.get('schedule_record_id')

                if schedule_record_id not in ['', None]:
                    action_scheduling_form = self.fourth_form_class(post_dict)
                    context['action_scheduling_form'] = action_scheduling_form

                    print(action_scheduling_form.errors)
                    if action_scheduling_form.is_valid():
                        import re
                        schedule_record = re.findall('\d+', schedule_record_id)

                        for s in schedule_record:
                            in_time = request.POST['in_time']
                            in_time = datetime.strptime(convert_time(in_time), '%I:%M %p')
                            in_time = in_time.strftime('%H:%M')
                            out_time = request.POST['out_time']
                            out_time = datetime.strptime(convert_time(out_time), '%I:%M %p')
                            out_time = out_time.strftime('%H:%M')

                            schedule_record_qs = ScheduleRecord.objects.filter(id=s)
                            out_date = request.POST['out_date']
                            if out_date not in ['', None]:
                                out_date = out_date
                            else:
                                out_date = schedule_record_qs[0].date

                            # check in time or date not greater than out time or date
                            if self.check_out_time(schedule_record_qs[0].date, in_time, out_date, out_time):
                                messages.error(request, "Out date or time should be greater than in time or date.")
                                # scheduling_list = self.get_instance()
                                context['scheduling_list'] = scheduling_list
                                return render(request, self.template_name, context)

                            # if any schedule has in time its working day will be true
                            is_working_day = True
                            schedule_record_qs.update(
                                is_working_day=is_working_day,
                                is_weekend=False if is_working_day is True else schedule_record_qs[0].is_weekend,
                                is_holiday=False if is_working_day is True else schedule_record_qs[0].is_holiday
                            )
                            time_record_qs = TimeTableRecord.objects.filter(schedule_record__id=s)
                            time_record_qs.update(in_time=in_time, out_date=out_date, out_time=out_time)

                            # break time record
                            break_start_temp = request.POST.getlist('__break_start')
                            break_start_date_temp = request.POST.getlist('__break_start_date')
                            break_end_temp = request.POST.getlist('__break_end')
                            break_end_date_temp = request.POST.getlist('__break_end_date')

                            break_time_qs = BreakTimeRecord.objects
                            break_time_qs.filter(timetable_record_id=time_record_qs[0].id).delete()
                            for j, start_time in enumerate(break_start_temp):
                                if start_time not in ['', None]:
                                    break_start = datetime.strptime(convert_time(start_time), '%I:%M %p')
                                    break_start = break_start.strftime('%H:%M')
                                    if break_start_date_temp[j] not in ['', None]:
                                        break_start_date = break_start_date_temp[j]
                                    else:
                                        break_start_date = schedule_record_qs[0].date

                                    # check break start time or date not greater than out time or date
                                    if self.check_out_time(break_start_date, break_start, out_date, out_time):
                                        messages.error(request,
                                                       "Break start date or time should not be "
                                                       "greater than end time or date.")
                                        # scheduling_list = self.get_instance()
                                        context['scheduling_list'] = scheduling_list
                                        return render(request, self.template_name, context)

                                    # check break start time or date not greater than in time or date
                                    if self.check_out_time(schedule_record_qs[0].date, in_time, break_start_date,
                                                           break_start):
                                        messages.error(request,
                                                       "Break start date or time should be "
                                                       "greater than in time or date.")
                                        # scheduling_list = self.get_instance()
                                        context['scheduling_list'] = scheduling_list
                                        return render(request, self.template_name, context)

                                    break_end_date = schedule_record_qs[0].date
                                    if break_end_temp[j] not in ['', None]:
                                        break_end = datetime.strptime(convert_time(break_end_temp[j]), '%I:%M %p')
                                        break_end = break_end.strftime('%H:%M')
                                        if break_end_date_temp[j] not in ['', None]:
                                            break_end_date = break_end_date_temp[j]
                                    else:
                                        break_end = None

                                    # check break end time or date not greater than out time or date
                                    if self.check_out_time(break_end_date, break_end, out_date, out_time):
                                        messages.error(request,
                                                       "Break start date or time should not be "
                                                       "greater than end time or date.")
                                        # scheduling_list = self.get_instance()
                                        context['scheduling_list'] = scheduling_list
                                        return render(request, self.template_name, context)

                                    # check break start time or date not greater than break end time or date
                                    if self.check_out_time(break_start_date, break_start, break_end_date, break_end):
                                        messages.error(request,
                                                       "Break end date or time should be greater "
                                                       "than break start time or date.")
                                        # scheduling_list = self.get_instance()
                                        context['scheduling_list'] = scheduling_list
                                        return render(request, self.template_name, context)

                                    break_time_qs.create(timetable_record_id=time_record_qs[0].id,
                                                         break_start=break_start,
                                                         break_start_date=break_start_date,
                                                         break_end=break_end,
                                                         break_end_date=break_end_date)
                        messages.success(request, "Saved successfully.")
                    else:
                        messages.error(request, "No data saved.")
                else:
                    messages.error(request, "No scheduling checked.")

        scheduling_list = self.get_instance()
        if scheduling_list:
            paginator = Paginator(scheduling_list, 50)
            page = self.request.GET.get('page')
            context['scheduling_list'] = paginator.get_page(page)
            index = context['scheduling_list'].number - 1
            max_index = len(paginator.page_range)
            start_index = index - 0 if index >= 3 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            context['page_range'] = list(paginator.page_range)[start_index:end_index]
            context['path'] = "%s" % "&".join(
                ["%s=%s" % (key, value) for (key, value) in self.request.GET.items()
                 if not key == 'page'])

        return render(request, self.template_name, context)

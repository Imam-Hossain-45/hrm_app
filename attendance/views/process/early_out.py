from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.views.generic import TemplateView, ListView, DetailView
from attendance.forms import *
from attendance.models import *
from helpers.mixins import PermissionMixin
from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from employees.models import EmployeeIdentification, LeaveManage
from django.http import JsonResponse
from helpers.functions import get_organizational_structure, get_employee_query_info
from .manual_attendance import convert_time
from leave.forms import SearchForm
from user_management.workflow import Approval
from user_management.models import Approval as ApprovalModel


def employeeFilter(employee, from_date, to_date, company, division, department, business_unit, branch, schedule):
    if employee not in ['', None] or from_date not in ['', None] or \
        to_date not in ['', None] or company not in ['', None] or \
        division not in ['', None] or department not in ['', None] or \
            business_unit not in ['', None] or branch not in ['', None] or schedule not in ['', None]:
        object_list = EarlyApplication.objects
        if employee not in ['', None]:
            object_list = object_list.filter(attendance__employee=employee)
        if from_date not in ['', None] and to_date not in ['', None]:
            object_list = object_list.filter(attendance__date__range=[from_date, to_date])
        if company not in ['', None]:
            object_list = object_list.filter(attendance__employee__employee_job_informations__company=company)
        if division not in ['', None]:
            object_list = object_list.filter(attendance__employee__employee_job_informations__division=division)
        if department not in ['', None]:
            object_list = object_list.filter(attendance__employee__employee_job_informations__department=department)
        if business_unit not in ['', None]:
            object_list = object_list.filter(
                attendance__employee__employee_job_informations__business_unit=business_unit)
        if schedule not in ['', None]:
            object_list = object_list.filter(attendance__employee__employee_attendance__schedule_type=schedule)
        mylist = object_list.order_by('-updated_at')
    else:
        mylist = EarlyApplication.objects.all().order_by('-updated_at')

    object_list = []
    if mylist:
        for early in mylist:
            early_apply_day = early.attendance
            timetable = TimeTable.objects.filter(
                schedule_master=early.attendance.employee.employee_attendance.last().schedule_type)
            em_deduction = LeaveManage.objects.filter(employee=early.attendance.employee)
            early_out_component = ''
            if em_deduction:
                is_deduction = em_deduction[0].deduction
                if is_deduction:
                    early_out_component = em_deduction[0].deduction_group.early_out_component
            if early.attendance.out_time is not None:
                out_time = early.attendance.out_time
            else:
                try:
                    early_application_qs = EarlyApplication.objects.get(attendance=early.attendance)
                    out_time = early_application_qs.early_out_time
                except Exception as e:
                    print(e)
                    out_time = None

            data = {
                'id': early.id,
                'created_at': early.created_at,
                'out_time': out_time,
                'date': early.attendance.out_date,
                'status': early.get_status_display(),
                'employee_id': early.attendance.employee.id,
                'name': early.attendance.employee,
                'designation': early.attendance.employee.employee_job_information.latest('updated_at'),
            }
            if timetable:
                for time_t in timetable:
                    if time_t.days.name == early_apply_day.date.strftime('%A'):
                        s_type = early.attendance.employee.employee_attendance.last().schedule_type.schedule_type
                        roster_type = early.attendance.employee.employee_attendance.last().schedule_type.roster_type
                        if early_out_component not in ['', None]:
                            duration = get_duration(s_type, time_t, early_apply_day, roster_type, out_time)
                            if duration != 0 and duration.seconds > 0:
                                split_t = str(duration).split(':')
                                duration = '{} hours, {} minutes'.format(split_t[0], split_t[1])
                            data['duration'] = duration
            object_list.append(data)
        return object_list


def get_duration(s_type, time_t, early_apply_day, roster_type, out_time):
    duration = 0
    if s_type in ['regular-fixed-time', 'fixed-day', 'weekly', 'day', 'freelencing']:
        schedule_time = datetime.combine(date.today(), time_t.out_time)
        if schedule_time.time() > out_time:
            duration = datetime.strptime(str(schedule_time.time()), "%H:%M:%S") - datetime.strptime(
                str(out_time),
                "%H:%M:%S")
    if s_type in ['roster'] and roster_type == 'fixed-roster':
        schedule_time = datetime.combine(date.today(), time_t.out_time)

        if schedule_time.time() > out_time:
            duration = datetime.strptime(str(schedule_time.time()), "%H:%M:%S") - datetime.strptime(
                str(out_time),
                "%H:%M:%S")
    if s_type in ['hourly']:
        time_duration = TimeDuration.objects.filter(timetable=time_t)
        closest_out_time = get_closest_to_dt(time_duration, early_apply_day.in_time).work_end
        schedule_time = datetime.combine(date.today(), closest_out_time)
        if schedule_time.time() > out_time:
            duration = datetime.strptime(str(schedule_time.time()), "%H:%M:%S") - datetime.strptime(
                str(out_time),
                "%H:%M:%S")
    return duration


def get_closest_to_dt(qs, dt):
    greater = qs.filter(work_start__gte=dt).order_by('work_start').first()
    less = qs.filter(work_start__lte=dt).order_by('-work_start').first()

    if greater and less:
        return greater if abs(
            datetime.strptime(str(greater.work_start), "%H:%M:%S") - datetime.strptime(str(dt), "%H:%M:%S")) < abs(
            datetime.strptime(str(less.work_start), "%H:%M:%S") - datetime.strptime(str(dt), "%H:%M:%S")) else less
    else:
        return greater or less


class EarlyApplicationList(LoginRequiredMixin, PermissionMixin, TemplateView):
    """
        show early out application list
        Access: Super-Admin, Admin
        Url: /admin/attendance/process/early_out_application/
    """
    template_name = 'attendance/process/early_out/list.html'
    permission_required = 'view_earlyapplication'

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

        application_list = employeeFilter(employee, from_date, to_date, company, division, department,
                                                business_unit, branch, schedule)
        if application_list:
            paginator = Paginator(application_list, 50)
            page = self.request.GET.get('page')
            context['early_out_application'] = paginator.get_page(page)
            index = context['early_out_application'].number - 1
            max_index = len(paginator.page_range)
            start_index = index - 0 if index >= 3 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            context['page_range'] = list(paginator.page_range)[start_index:end_index]
            context['path'] = "%s" % "&".join(["%s=%s" % (key, value) for (key, value) in self.request.GET.items()
                                               if not key == 'page'])

        context['objects'] = application_list

        return context


class EarlyOutCreateView(LoginRequiredMixin, PermissionMixin, TemplateView):
    """
        Add new Leave entry
        Access: Super-Admin, Admin
        Url: /admin/leave/leave_entry/new
    """
    template_name = 'attendance/process/early_out/create.html'
    permission_required = ['add_earlyapplication', 'change_earlyapplication', 'view_earlyapplication',
                           'delete_earlyapplication']

    def get_query_information(self, query):
        duration = 0
        try:
            emp = EmployeeIdentification.objects.get(id=query)
            job = emp.employee_job_information.latest('updated_at') if emp.employee_job_information.exists() else ''
            information = {
                'name': emp,
                'designation': job.designation.name if job not in EMPTY_VALUES and
                job.designation not in EMPTY_VALUES else '',
                'employee_id': emp.employee_id,
                'schedule_type': emp.employee_attendance.last().schedule_type
                if emp.employee_attendance.last() is not None else None,
                'company': job.company.name if job not in EMPTY_VALUES and job.company not in EMPTY_VALUES else '',
                'division': job.division.name if job not in EMPTY_VALUES and job.division not in EMPTY_VALUES else '',
                'department': job.department.name if job not in EMPTY_VALUES and
                job.department not in EMPTY_VALUES else '',
                'business_unit': job.business_unit.name if job not in EMPTY_VALUES and
                job.business_unit not in EMPTY_VALUES else '',
                'project': job.project.name if job not in EMPTY_VALUES and job.project not in EMPTY_VALUES else ''
            }
            early_apply = EarlyApplication.objects.filter(attendance__employee_id=query)
            last_apply = early_apply.last()

            out_time = ''
            data = {}
            if last_apply is not None:
                if last_apply.attendance.out_time is not None:
                    out_time = last_apply.attendance.out_time
                else:
                    out_time = last_apply.early_out_time
                data = {
                    'out_date': last_apply.attendance.out_date
                    if last_apply.attendance.out_date not in EMPTY_VALUES else last_apply.attendance.date,
                    'out_time': out_time,
                    'status': last_apply.get_status_display(),
                }

            early_list = {
                'applied': early_apply.count(),
                'approved': early_apply.filter(status='approved').count(),
                'declined': early_apply.filter(status='declined').count(),
                'pending': early_apply.filter(status='pending').count(),
            }

            if last_apply:
                early_apply_day = last_apply.attendance
                timetable = TimeTable.objects.filter(schedule_master=emp.employee_attendance.last().schedule_type)
                em_deduction = LeaveManage.objects.filter(employee_id=emp)
                early_out_component = ''
                if em_deduction:
                    is_deduction = em_deduction[0].deduction
                    if is_deduction:
                        early_out_component = em_deduction[0].deduction_group.early_out_component
                if timetable:
                    for time_t in timetable:
                        if time_t.days.name == early_apply_day.date.strftime('%A'):
                            s_type = emp.employee_attendance.last().schedule_type.schedule_type
                            roster_type = emp.employee_attendance.last().schedule_type.roster_type
                            if early_out_component not in ['', None]:
                                if last_apply is not None:
                                    duration = get_duration(s_type, time_t, early_apply_day, roster_type, out_time)
                                    if duration != 0 and duration.seconds > 0:
                                        split_t = str(duration).split(':')
                                        duration = '{} hours, {} minutes'.format(split_t[0], split_t[1])
            return information, early_list, data, duration
        except Exception as e:
            # raise e
            return e

    def get_instance(self):
        if self.kwargs.get('pk'):
            return get_object_or_404(EarlyApplication, Q(status='pending'), pk=self.kwargs['pk'])

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
                info, early_list, early_apply, duration = info_qs
                context['info'] = info
                context['early_list'] = early_list
                context['early_apply'] = early_apply
                context['duration'] = duration

                application_instance = self.get_instance()
                if application_instance:
                    if application_instance.attendance.out_time is not None:
                        out_time = application_instance.attendance.out_time
                    else:
                        try:
                            early_application_qs = EarlyApplication.objects.\
                                get(attendance=application_instance.attendance)
                            out_time = early_application_qs.early_out_time
                        except:
                            out_time = None
                    context['form'] = EarlyOutForm(query, initial={'attendance': application_instance.attendance.id,
                                                                   'early_out_time': out_time,
                                                                   'entry_date': application_instance.attendance.date},
                                                   instance=application_instance)
                    context['edit'] = True
                else:
                    context['form'] = EarlyOutForm(query)
            except TypeError:
                context['error'] = info_qs
        context['employee'] = query
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
            info, early_list, early_apply, duration = self.get_query_information(query)
            context['info'] = info
            context['early_list'] = early_list
            context['early_apply'] = early_apply
            context['duration'] = duration
            obj = self.get_instance()
            if obj:
                context['form'] = EarlyOutForm(query, request.POST, files=request.FILES,
                                               initial={'attendance': self.get_instance().attendance.id,
                                                        'early_out_time': self.get_instance().attendance.out_time,
                                                        'entry_date': self.get_instance().attendance.date},
                                               instance=obj)
                context['edit'] = True
            else:
                context['form'] = EarlyOutForm(query, request.POST, files=request.FILES)
            context['employee'] = query

            if request.POST:
                post_dict = self.request.POST.copy()
                post_dict['early_out_time'] = ''
                if self.request.POST.get('early_out_time').strip() not in ['', None]:
                    post_dict['early_out_time'] = datetime.strptime(convert_time(self.request.POST['early_out_time']),
                                                                    '%I:%M %p').time()
                    post_dict['early_out_time'] = post_dict['early_out_time'].strftime('%H:%M')

                form = EarlyOutForm(query, post_dict, files=request.FILES, instance=obj)
                context['form'] = form
                previous_early_application = False
                if request.POST['attendance']:
                    attendance_id = request.POST['attendance']
                    early_application_qs = EarlyApplication.objects.filter(attendance_id=attendance_id,
                                                                           status__in=['declined', 'approved'])

                    if early_application_qs:
                        messages.error(self.request, "This early out application already %s."
                                       % (early_application_qs[0].get_status_display()))
                        previous_early_application = True

                if form.is_valid() and previous_early_application is False:
                    form = form.save(commit=False)
                    form.attendance_id = request.POST['attendance']
                    form.reason_of_early_out = request.POST['reason_of_early_out']
                    form.early_out_time = post_dict['early_out_time']
                    if 'apply' in request.POST:
                        form.status = 'pending'
                        form.save()
                    elif 'apply_approve' in request.POST:
                        form.status = 'approved'
                        form.save()
                        daily_record = DailyRecord.objects.filter(
                            schedule_record__employee=form.attendance.employee,
                            schedule_record__date=form.attendance.date)
                        if daily_record.exists():
                            late = daily_record[0].late
                            early_out = False
                            if late or early_out:
                                under_work = True
                            else:
                                under_work = False
                            daily_record.update(early=early_out, is_present=True, under_work=under_work)
                    else:
                        form.status = 'declined'
                        form.save()

                    messages.success(self.request, "Successfully applied.")
                    return redirect('beehive_admin:attendance:early_out_application_list')
        return render(request, self.template_name, context)


class EarlyOutDetailsView(LoginRequiredMixin, PermissionMixin, DetailView):
    template_name = 'attendance/process/early_out/details.html'
    permission_required = 'view_earlyapplication'
    model = EarlyApplication

    def get_query_information(self, query):
        duration = 0
        try:
            emp = EmployeeIdentification.objects.get(id=query)
            job = emp.employee_job_information.latest('updated_at') if emp.employee_job_information.exists() else ''
            information = {
                'name': emp,
                'designation': job.designation.name if job not in EMPTY_VALUES and
                job.designation not in EMPTY_VALUES else '',
                'employee_id': emp.employee_id,
                'schedule_type': emp.employee_attendance.last().schedule_type
                if emp.employee_attendance.last() is not None else None,
                'company': job.company.name if job not in EMPTY_VALUES and job.company not in EMPTY_VALUES else '',
                'division': job.division.name if job not in EMPTY_VALUES and job.division not in EMPTY_VALUES else '',
                'department': job.department.name if job not in EMPTY_VALUES and
                job.department not in EMPTY_VALUES else '',
                'business_unit': job.business_unit.name if job not in EMPTY_VALUES and
                job.business_unit not in EMPTY_VALUES else '',
                'project': job.project.name if job not in EMPTY_VALUES and job.project not in EMPTY_VALUES else ''
            }
            early_apply = EarlyApplication.objects.filter(attendance__employee_id=query)
            last_apply = early_apply.last()

            out_time = ''
            data = {}
            if last_apply is not None:
                if last_apply.attendance.out_time is not None:
                    out_time = last_apply.attendance.out_time
                else:
                    out_time = last_apply.early_out_time
                data = {
                    'out_date': last_apply.attendance.out_date
                    if last_apply.attendance.out_date not in EMPTY_VALUES else last_apply.attendance.date,
                    'out_time': out_time,
                    'status': last_apply.get_status_display(),
                }

            early_list = {
                'applied': early_apply.count(),
                'approved': early_apply.filter(status='approved').count(),
                'declined': early_apply.filter(status='declined').count(),
                'pending': early_apply.filter(status='pending').count(),
            }

            if last_apply:
                early_apply_day = last_apply.attendance
                timetable = TimeTable.objects.filter(schedule_master=emp.employee_attendance.last().schedule_type)
                em_deduction = LeaveManage.objects.filter(employee_id=emp)
                early_out_component = ''
                if em_deduction:
                    is_deduction = em_deduction[0].deduction
                    if is_deduction:
                        early_out_component = em_deduction[0].deduction_group.early_out_component
                if timetable:
                    for time_t in timetable:
                        if time_t.days.name == early_apply_day.date.strftime('%A'):
                            s_type = emp.employee_attendance.last().schedule_type.schedule_type
                            roster_type = emp.employee_attendance.last().schedule_type.roster_type
                            if early_out_component not in ['', None]:
                                if last_apply is not None:
                                    duration = get_duration(s_type, time_t, early_apply_day, roster_type, out_time)
                                    if duration != 0 and duration.seconds > 0:
                                        split_t = str(duration).split(':')
                                        duration = '{} hours, {} minutes'.format(split_t[0], split_t[1])
            return information, early_list, data, duration
        except Exception as e:
            # raise e
            return e

    def get_instance(self):
        if self.kwargs.get('pk'):
            return get_object_or_404(EarlyApplication, Q(status__in=['declined', 'approved']), pk=self.kwargs['pk'])

    def get_early_information(self):
        early = self.get_instance()
        early_apply_day = early.attendance
        timetable = TimeTable.objects.filter(
            schedule_master=early.attendance.employee.employee_attendance.last().schedule_type)
        em_deduction = LeaveManage.objects.filter(employee=early.attendance.employee)
        early_out_component = ''
        if em_deduction:
            is_deduction = em_deduction[0].deduction
            if is_deduction:
                early_out_component = em_deduction[0].deduction_group.early_out_component
        if early_apply_day.out_time is not None:
            out_time = early_apply_day.out_time
        else:
            try:
                early_application_qs = EarlyApplication.objects. \
                    get(attendance=early_apply_day)
                out_time = early_application_qs.early_out_time
            except:
                out_time = None

        data = {
            'created_at': early.created_at,
            'out_date': early.attendance.out_date
            if early.attendance.out_date not in EMPTY_VALUES else early.attendance.out_date,
            'out_time': out_time,
            'reason': early.reason_of_early_out,
            'attachment': early.attachment,
            'attachment_url': early.attachment.url if early.attachment not in EMPTY_VALUES else '',
            'status': early.get_status_display(),
        }
        if timetable:
            for time_t in timetable:
                if time_t.days.name == early_apply_day.date.strftime('%A'):
                    s_type = early.attendance.employee.employee_attendance.last().schedule_type.schedule_type
                    roster_type = early.attendance.employee.employee_attendance.last().schedule_type.roster_type
                    if early_out_component not in ['', None]:
                        duration = get_duration(s_type, time_t, early_apply_day, roster_type, out_time)
                        if duration != 0 and duration.seconds > 0:
                            split_t = str(duration).split(':')
                            duration = '{} hours, {} minutes'.format(split_t[0], split_t[1])
                        data['duration'] = duration
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
                info, early_list, early_apply, duration = info_qs
                context['info'] = info
                context['early_list'] = early_list
                context['early_apply'] = early_apply
                context['duration'] = duration
                context['early_info'] = self.get_early_information()
                context['comment'] = EarlyApprovalComment.objects.filter(early_out=self.kwargs['pk'])
            except TypeError:
                context['error'] = info_qs
        context['employee'] = query
        return context


class OutTimeView(LoginRequiredMixin, PermissionMixin, TemplateView):
    """
        get time by ajax
    """

    def get(self, request, *args):
        query = request.GET.get('query')
        date = request.GET.get('date')
        attendance_time = AttendanceData.objects.filter(employee_id=query, date=date).last()
        if attendance_time:
            id = attendance_time.id
            if attendance_time.out_time is None:
                try:
                    temp_out_time = EarlyApplication.objects.get(attendance=attendance_time)
                    temp_out_time = temp_out_time.early_out_time
                except:
                    temp_out_time = ''
            else:
                temp_out_time = attendance_time.out_time
            if temp_out_time is not '':
                temp = datetime.combine(attendance_time.date, temp_out_time)
                out_time = datetime.strftime(temp, '%I:%M %p')
            else:
                out_time = None
        else:
            id = None
            out_time = None
        data = {'attendance_id': id, 'out_time': out_time}
        return JsonResponse(data)


class EarlyOutIndividualListView(LoginRequiredMixin, PermissionMixin, ListView):
    """
        show individual employee late application list
        Access: Super-Admin, Admin
        Url: /admin/attendance/process/early_out/list/?query=pk
    """
    template_name = 'attendance/process/early_out/individual_list.html'
    model = EarlyApplication
    permission_required = 'view_earlyapplication'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        object_list = []
        mylist = EarlyApplication.objects.filter(attendance__employee_id=self.kwargs['pk']).order_by('-updated_at')
        if mylist:
            emp = EmployeeIdentification.objects.get(id=self.kwargs['pk'])
            timetable = TimeTable.objects.filter(schedule_master=emp.employee_attendance.last().schedule_type)
            em_deduction = LeaveManage.objects.filter(employee_id=emp)
            early_out_component = ''
            if em_deduction:
                is_deduction = em_deduction[0].deduction
                if is_deduction:
                    early_out_component = em_deduction[0].deduction_group.early_out_component
            for early in mylist:
                if early.attendance.out_time is not None:
                    out_time = early.attendance.out_time
                else:
                    try:
                        early_application_qs = EarlyApplication.objects.get(attendance=early.attendance)
                        out_time = early_application_qs.early_out_time
                    except:
                        out_time = None
                data = {
                    'id': early.id,
                    'created': early.created_at,
                    'out_time': out_time,
                    'out_date': early.attendance.out_date
                    if early.attendance.out_date not in EMPTY_VALUES else early.attendance.date,
                    'status': early.get_status_display(),
                    'employee_id': self.kwargs['pk'],
                }
                early_apply_day = early.attendance
                if timetable:
                    for time_t in timetable:
                        if time_t.days.name == early_apply_day.date.strftime('%A'):
                            s_type = emp.employee_attendance.last().schedule_type.schedule_type
                            roster_type = emp.employee_attendance.last().schedule_type.roster_type
                            if early_out_component not in ['', None]:
                                duration = get_duration(s_type, time_t, early_apply_day, roster_type, out_time)
                                if duration != 0 and duration.seconds > 0:
                                    split_t = str(duration).split(':')
                                    duration = '{} hours, {} minutes'.format(split_t[0], split_t[1])
                                data['duration'] = duration
                object_list.append(data)

        context['job'] = mylist.last().attendance.employee.employee_job_information.latest('updated_at')

        if object_list:
            paginator = Paginator(object_list, 50)
            page = self.request.GET.get('page')
            context['early_out_application'] = paginator.get_page(page)
            index = context['early_out_application'].number - 1
            max_index = len(paginator.page_range)
            start_index = index - 0 if index >= 3 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            context['page_range'] = list(paginator.page_range)[start_index:end_index]

        context['objects'] = object_list

        return context


class EarlyPendingListView(LoginRequiredMixin, PermissionMixin, ListView):
    """
        show pending late application list
        Access: Super-Admin, Admin
        Url: /admin/attendance/early_out_approval/list/
    """
    template_name = 'attendance/process/early_approval/list.html'
    model = EarlyApplication
    permission_required = 'view_earlyapplication'

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

        if employee not in ['', None] or from_date not in ['', None] or to_date not in ['', None] or \
            company not in ['', None] or division not in ['', None] or department not in ['', None] or \
                business_unit not in ['', None] or branch not in ['', None] or schedule not in ['', None]:
            object_list = EarlyApplication.objects.filter(status='pending')
            if employee not in ['', None]:
                object_list = object_list.filter(attendance__employee=employee)
            if from_date not in ['', None] and to_date not in ['', None]:
                object_list = object_list.filter(attendance__date__range=[from_date, to_date])
            if company not in ['', None]:
                object_list = object_list.filter(attendance__employee__employee_job_informations__company=company)
            if division not in ['', None]:
                object_list = object_list.filter(attendance__employee__employee_job_informations__division=division)
            if department not in ['', None]:
                object_list = object_list.filter(attendance__employee__employee_job_informations__department=department)
            if business_unit not in ['', None]:
                object_list = object_list.filter(
                    attendance__employee__employee_job_informations__business_unit=business_unit)
            if schedule not in ['', None]:
                object_list = object_list.filter(attendance__employee__employee_attendance__schedule_type=schedule)
            mylist = object_list.order_by('-updated_at')
        else:
            mylist = EarlyApplication.objects.filter(status='pending').order_by('-updated_at')
        object_list = []
        if mylist:
            for early in mylist:
                early_apply_day = early.attendance
                timetable = TimeTable.objects.filter(
                    schedule_master=early.attendance.employee.employee_attendance.last().schedule_type)
                em_deduction = LeaveManage.objects.filter(employee=early_apply_day.employee)
                early_out_component = ''
                if em_deduction:
                    is_deduction = em_deduction[0].deduction
                    if is_deduction:
                        early_out_component = em_deduction[0].deduction_group.early_out_component

                if early_apply_day.out_time is not None:
                    out_time = early_apply_day.out_time
                else:
                    try:
                        early_application_qs = EarlyApplication.objects. \
                            get(attendance=early_apply_day)
                        out_time = early_application_qs.early_out_time
                    except:
                        out_time = None

                data = {
                    'id': early.id,
                    'out_time': out_time,
                    'out_date': early.attendance.out_date
                    if early.attendance.out_date not in EMPTY_VALUES else early.attendance.date,
                    'status': early.get_status_display(),
                    'employee_id': early_apply_day.employee.id,
                    'name': early_apply_day.employee,
                    'designation': early_apply_day.employee.employee_job_information.latest('updated_at'),
                }
                if timetable:
                    for time_t in timetable:
                        if time_t.days.name == early_apply_day.date.strftime('%A'):
                            s_type = early.attendance.employee.employee_attendance.last().schedule_type.schedule_type
                            roster_type = early.attendance.employee.employee_attendance.last().schedule_type.roster_type
                            if early_out_component not in ['', None]:
                                duration = get_duration(s_type, time_t, early_apply_day, roster_type, out_time)
                                if duration != 0 and duration.seconds > 0:
                                    split_t = str(duration).split(':')
                                    duration = '{} hours, {} minutes'.format(split_t[0], split_t[1])
                                data['duration'] = duration
                object_list.append(data)

        if object_list:
            paginator = Paginator(object_list, 50)
            page = self.request.GET.get('page')
            context['early_out_application'] = paginator.get_page(page)
            index = context['early_out_application'].number - 1
            max_index = len(paginator.page_range)
            start_index = index - 0 if index >= 3 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            context['page_range'] = list(paginator.page_range)[start_index:end_index]
            context['path'] = "%s" % "&".join(["%s=%s" % (key, value) for (key, value) in self.request.GET.items()
                                               if not key == 'page'])

        context['objects'] = object_list

        return context


class EarlyApprovalView(LoginRequiredMixin, PermissionMixin, TemplateView):
    """
        Late early_approval form
        Access: Super-Admin, Admin
        Url: /admin/attendance/process/early_out_approval/<pk>/
    """
    template_name = 'attendance/process/early_approval/create.html'
    permission_required = 'change_earlyapplication'

    def get_employee_information(self):
        emp = self.get_instance().attendance.employee
        job = emp.employee_job_information.latest('updated_at')
        information = {
            'name': emp,
            'designation': job.designation.name if job.designation not in EMPTY_VALUES else '',
            'employee_id': emp.employee_id,
            'schedule_type': emp.employee_attendance.last().schedule_type,
            'company': job.company.name if job.company not in EMPTY_VALUES else '',
            'division': job.division.name if job.division not in EMPTY_VALUES else '',
            'department': job.department.name if job.department not in EMPTY_VALUES else '',
            'business_unit': job.business_unit.name if job.business_unit not in EMPTY_VALUES else '',
            'project': job.project.name if job.project not in EMPTY_VALUES else ''
        }
        return information

    def get_early_information(self):
        early = self.get_instance()
        early_apply_day = early.attendance
        timetable = TimeTable.objects.filter(
            schedule_master=early.attendance.employee.employee_attendance.last().schedule_type)
        em_deduction = LeaveManage.objects.filter(employee=early.attendance.employee)
        early_out_component = ''
        if em_deduction:
            is_deduction = em_deduction[0].deduction
            if is_deduction:
                early_out_component = em_deduction[0].deduction_group.early_out_component
        if early_apply_day.out_time is not None:
            out_time = early_apply_day.out_time
        else:
            try:
                early_application_qs = EarlyApplication.objects. \
                    get(attendance=early_apply_day)
                out_time = early_application_qs.early_out_time
            except:
                out_time = None

        data = {
            'created_at': early.created_at,
            'out_time': out_time,
            'out_date': early.attendance.out_date
            if early.attendance.out_date not in EMPTY_VALUES else early.attendance.date,
            'reason': early.reason_of_early_out,
            'attachment': early.attachment,
            'attachment_url': early.attachment.url if early.attachment not in EMPTY_VALUES else '',
        }
        if timetable:
            for time_t in timetable:
                if time_t.days.name == early_apply_day.date.strftime('%A'):
                    s_type = early.attendance.employee.employee_attendance.last().schedule_type.schedule_type
                    roster_type = early.attendance.employee.employee_attendance.last().schedule_type.roster_type
                    if early_out_component not in ['', None]:
                        duration = get_duration(s_type, time_t, early_apply_day, roster_type, out_time)
                        if duration != 0 and duration.seconds > 0:
                            split_t = str(duration).split(':')
                            duration = '{} hours, {} minutes'.format(split_t[0], split_t[1])
                        data['duration'] = duration
        return data

    def get_instance(self):
        return get_object_or_404(EarlyApplication, Q(status='pending'), pk=self.kwargs['pk'])

    def get_comment(self):
        return EarlyApprovalComment.objects.filter(early_out=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        entry = self.kwargs.get('pk')
        if entry is not None:
            context['employee_info'] = self.get_employee_information()
            context['early_info'] = self.get_early_information()
            context['form'] = EarlyApprovalForm()
            context['comment'] = self.get_comment()
        return context

    def post(self, request, *args, **kwargs):
        context = dict()
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        entry = self.kwargs.get('pk')
        if entry is not None:
            context['employee_info'] = self.get_employee_information()
            context['early_info'] = self.get_early_information()
            context['form'] = EarlyApprovalForm(request.POST)
            context['comment'] = self.get_comment()

        if 'save_comment' in request.POST:
            form = EarlyApprovalForm(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                form.user = request.user
                form.early_out_id = entry
                form.save()
                return redirect('beehive_admin:attendance:early_approval_form', entry)
        if 'decline' in request.POST:
            approval = Approval(request)
            approval.approve_or_decline('declined', 'early-out', entry)

            approvals = ApprovalModel.objects.filter(
                item=entry,
                item_type='early-out'
            )
            declined_approvals = list(filter(lambda approval: approval.status == 'declined', approvals))

            if approvals.count() == len(declined_approvals):
                EarlyApplication.objects.filter(id=entry).update(status='declined')
                approval.set_notifications(
                    notification_for=entry,
                    content='Early out declined'
                )

            return redirect('beehive_admin:attendance:early_out_application_list')
        if 'approve' in request.POST:
            early_approve = EarlyApplication.objects.filter(id=entry)
            approval = Approval(request)
            approval.approve_or_decline('declined', 'early-out', entry)

            approvals = ApprovalModel.objects.filter(
                item=entry,
                item_type='early-out'
            )
            declined_approvals = list(filter(lambda approval: approval.status == 'declined', approvals))

            if approvals.count() == len(declined_approvals):
                early_approve.update(status='approved')
                daily_record = DailyRecord.objects.filter(schedule_record__employee=early_approve[0].attendance.employee,
                                                          schedule_record__date=early_approve[0].attendance.date)

                approval.set_notifications(
                    notification_for=entry,
                    content='Early out approved'
                )

                if daily_record.exists():
                    late = daily_record[0].late
                    early_out = False
                    if late or early_out:
                        under_work = True
                    else:
                        under_work = False
                    daily_record.update(early=early_out, is_present=True, under_work=under_work)
            return redirect('beehive_admin:attendance:early_out_application_list')

        return render(request, self.template_name, context)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
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
from leave.forms import SearchForm
from user_management.workflow import Approval
from user_management.models import Approval as ApprovalModel, ApprovalNotification


def employeeFilter(employee, from_date, to_date, company, division, department, business_unit, branch, schedule):
    if employee not in ['', None] or from_date not in ['', None] or \
        to_date not in ['', None] or company not in ['', None] or \
        division not in ['', None] or department not in ['', None] or \
        business_unit not in ['', None] or branch not in ['', None] or \
            schedule not in ['', None]:
        object_list = LateApplication.objects
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
        mylist = LateApplication.objects.all().order_by('-updated_at')

    object_list = []
    if mylist:
        for late in mylist:
            late_apply_day = late.attendance
            timetable = TimeTable.objects.filter(
                schedule_master=late.attendance.employee.employee_attendance.last().schedule_type)
            em_deduction = LeaveManage.objects.filter(employee=late.attendance.employee)
            late_component = ''
            if em_deduction:
                is_deduction = em_deduction[0].deduction
                if is_deduction:
                    late_component = em_deduction[0].deduction_group.late_component

            data = {
                'id': late.id,
                'in_date': late.attendance.date,
                'in_time': late.attendance.in_time,
                'status': late.get_status_display(),
                'employee_id': late.attendance.employee.id,
                'name': late.attendance.employee,
                'designation': late.attendance.employee.employee_job_information.latest('updated_at'),
            }
            if timetable:
                for time_t in timetable:
                    if time_t.days.name == late_apply_day.date.strftime('%A'):
                        s_type = late.attendance.employee.employee_attendance.last().schedule_type.schedule_type
                        roster_type = late.attendance.employee.employee_attendance.last().schedule_type.roster_type
                        if late_component not in ['', None]:
                            try:
                                late_duration = get_late_duration(s_type, time_t, late_apply_day, roster_type)
                                if late_duration != 0 and late_duration.seconds > 0:
                                    split_t = str(late_duration).split(':')
                                    late_duration = '{} hours, {} minutes'.format(split_t[0], split_t[1])
                                data['late_duration'] = late_duration
                            except:
                                pass
            object_list.append(data)

        return object_list


def get_late_duration(s_type, time_t, late_apply_day, roster_type):
    late_duration = 0
    if s_type in ['regular-fixed-time', 'fixed-day', 'weekly', 'day', 'freelencing']:
        schedule_time = datetime.combine(date.today(), time_t.in_time)
        if late_apply_day.in_time > schedule_time.time():
            late_duration = datetime.strptime(str(late_apply_day.in_time),
                                              "%H:%M:%S") - datetime.strptime(
                str(schedule_time.time()), "%H:%M:%S")
    if s_type in ['roster'] and roster_type == 'fixed-roster':
        schedule_time = datetime.combine(date.today(), time_t.in_time)
        if late_apply_day.in_time > schedule_time.time():
            late_duration = datetime.strptime(str(late_apply_day.in_time),
                                              "%H:%M:%S") - datetime.strptime(
                str(schedule_time.time()), "%H:%M:%S")
    if s_type in ['hourly']:
        time_duration = TimeDuration.objects.filter(timetable=time_t)
        closest_in_time = get_closest_to_dt(time_duration, late_apply_day.in_time).work_start
        schedule_time = datetime.combine(date.today(), closest_in_time)
        if late_apply_day.in_time > schedule_time.time():
            late_duration = datetime.strptime(str(late_apply_day.in_time),
                                              "%H:%M:%S") - datetime.strptime(
                str(schedule_time.time()), "%H:%M:%S")

    return late_duration


def get_closest_to_dt(qs, dt):
    greater = qs.filter(work_start__gte=dt).order_by('work_start').first()
    less = qs.filter(work_start__lte=dt).order_by('-work_start').first()

    if greater and less:
        return greater if abs(
            datetime.strptime(str(greater.work_start), "%H:%M:%S") - datetime.strptime(str(dt), "%H:%M:%S")) < abs(
            datetime.strptime(str(less.work_start), "%H:%M:%S") - datetime.strptime(str(dt), "%H:%M:%S")) else less
    else:
        return greater or less


class LateApplicationList(LoginRequiredMixin, PermissionMixin, ListView):
    """
        show Late entry application list
        Access: Super-Admin, Admin
        Url: /admin/attendance/process/late_entry_application/
    """
    template_name = 'attendance/process/late_entry/list.html'
    permission_required = 'view_lateapplication'
    model = LateApplication
    context_object_name = 'late_application'

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
            context['late_application'] = paginator.get_page(page)
            index = context['late_application'].number - 1
            max_index = len(paginator.page_range)
            start_index = index - 0 if index >= 3 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            context['page_range'] = list(paginator.page_range)[start_index:end_index]
            context['path'] = "%s" % "&".join(["%s=%s" % (key, value) for (key, value) in self.request.GET.items()
                                               if not key == 'page'])

        context['objects'] = application_list

        return context


class LateEntryCreateView(LoginRequiredMixin, PermissionMixin, TemplateView):
    """
        Add new Leave entry
        Access: Super-Admin, Admin
        Url: /admin/leave/leave_entry/new
    """
    template_name = 'attendance/process/late_entry/create.html'
    permission_required = ['add_lateapplication', 'change_lateapplication', 'view_lateapplication',
                           'delete_lateapplication']

    def get_query_information(self, query):
        late_duration = 0
        try:
            emp = EmployeeIdentification.objects.get(id=query)
            job = emp.employee_job_information.latest('updated_at') if emp.employee_job_information.exists() else ''
            information = {
                'name': emp,
                'designation': job.designation.name if job not in EMPTY_VALUES and
                job.designation not in EMPTY_VALUES else '',
                'employee_id': emp.employee_id,
                'schedule_type': emp.employee_attendance.last().schedule_type,
                'company': job.company.name if job not in EMPTY_VALUES and job.company not in EMPTY_VALUES else '',
                'division': job.division.name if job not in EMPTY_VALUES and job.division not in EMPTY_VALUES else '',
                'department': job.department.name if job not in EMPTY_VALUES and
                job.department not in EMPTY_VALUES else '',
                'business_unit': job.business_unit.name if job not in EMPTY_VALUES and
                job.business_unit not in EMPTY_VALUES else '',
                'project': job.project.name if job not in EMPTY_VALUES and job.project not in EMPTY_VALUES else ''
            }
            late_apply = LateApplication.objects.filter(attendance__employee_id=query)

            late_list = {
                'applied': late_apply.count(),
                'approved': late_apply.filter(status='approved').count(),
                'declined': late_apply.filter(status='declined').count(),
                'pending': late_apply.filter(status='pending').count(),
            }

            if late_apply:
                late_apply_day = late_apply.last().attendance
                timetable = TimeTable.objects.filter(schedule_master=emp.employee_attendance.last().schedule_type)
                em_deduction = LeaveManage.objects.filter(employee=emp)
                late_component = ''
                if em_deduction:
                    is_deduction = em_deduction[0].deduction
                    if is_deduction:
                        late_component = em_deduction[0].deduction_group.late_component
                if timetable:
                    for time_t in timetable:
                        if time_t.days.name == late_apply_day.date.strftime('%A'):
                            s_type = emp.employee_attendance.last().schedule_type.schedule_type
                            roster_type = emp.employee_attendance.last().schedule_type.roster_type
                            if late_component not in ['', None]:
                                late_duration = get_late_duration(s_type, time_t, late_apply_day, roster_type)
                                if late_duration != 0 and late_duration.seconds > 0:
                                    split_t = str(late_duration).split(':')
                                    late_duration = '{} hours, {} minutes'.format(split_t[0], split_t[1])
            return information, late_list, late_apply, late_duration
        except Exception as e:
            return e

    def get_instance(self):
        if self.kwargs.get('pk'):
            return get_object_or_404(LateApplication, Q(status='pending'), pk=self.kwargs['pk'])

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

        context['employee'] = query
        if query is not None:
            info_qs = self.get_query_information(query)
            try:
                info, late_list, late_apply, late_duration = info_qs
                context['info'] = info
                context['late_list'] = late_list
                context['late_apply'] = late_apply
                context['late_duration'] = late_duration
                late_qs = self.get_instance()
                if late_qs:
                    context['form'] = LateEntryForm(query, initial={'attendance': late_qs.attendance.id,
                                                                    'entry_time': late_qs.attendance.in_time,
                                                                    'entry_date': late_qs.attendance.date},
                                                    instance=late_qs)
                    context['edit'] = True
                else:
                    context['form'] = LateEntryForm(query)
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

        context['employee'] = query
        if query is not None:
            info, late_list, late_apply, late_duration = self.get_query_information(query)
            context['info'] = info
            context['late_list'] = late_list
            context['late_apply'] = late_apply
            context['late_duration'] = late_duration
            obj = self.get_instance()
            if obj:
                context['form'] = LateEntryForm(query, request.POST, files=request.FILES,
                                                initial={'attendance': obj.attendance.id,
                                                         'entry_time': obj.attendance.in_time,
                                                         'entry_date': obj.attendance.date},
                                                instance=obj)
                context['edit'] = True
            else:
                context['form'] = LateEntryForm(query, request.POST, files=request.FILES)

            if request.POST:
                form = LateEntryForm(query, data=request.POST, files=request.FILES,
                                     instance=obj)
                previous_late_application = False

                if request.POST['attendance']:
                    attendance_id = request.POST['attendance']
                    late_application_qs = LateApplication.objects.filter(attendance_id=attendance_id,
                                                                         status__in=['declined', 'approved'])
                    if late_application_qs:
                        messages.error(self.request, "This late entry already %s."
                                       % (late_application_qs[0].get_status_display()))
                        time_data = AttendanceData.objects.filter(employee_id=query,
                                                                  date=request.POST.get('entry_date')).last()
                        if time_data:
                            in_time = time_data.in_time
                        else:
                            in_time = ''
                        context['form'] = LateEntryForm(query, data=request.POST, files=request.FILES,
                                                        initial={'entry_time': in_time},
                                                        instance=obj)
                        previous_late_application = True
                if form.is_valid() and previous_late_application is False:
                    form = form.save(commit=False)
                    form.attendance_id = request.POST['attendance']
                    form.reason_of_late = request.POST['reason_of_late']
                    if 'apply' in request.POST:
                        form.status = 'pending'
                        form.save()
                    elif 'apply_approve' in request.POST:
                        form.status = 'approved'
                        form.save()
                        daily_record = DailyRecord.objects.\
                            filter(schedule_record__employee_id=query,
                                   schedule_record__date=form.attendance.date)
                        if daily_record.exists():
                            early_out = daily_record[0].early
                            late = False
                            if late or early_out:
                                under_work = True
                            else:
                                under_work = False
                            daily_record.update(late=late, is_present=True, under_work=under_work)
                    else:
                        form.status = 'declined'
                        form.save()

                    messages.success(self.request, "Successfully applied.")
                    return redirect('beehive_admin:attendance:late_entry_application_list')
                else:
                    time_data = AttendanceData.objects.filter(employee_id=query,
                                                              date=request.POST.get('entry_date')).last()
                    if time_data:
                        in_time = time_data.in_time
                    else:
                        in_time = ''
                    context['form'] = LateEntryForm(query, data=request.POST, files=request.FILES,
                                         initial={'entry_time': in_time},
                                         instance=obj)
        return render(request, self.template_name, context)


class LateEntryDetailsView(LoginRequiredMixin, PermissionMixin, DetailView):
    template_name = 'attendance/process/late_entry/details.html'
    permission_required = 'view_lateapplication'
    model = LateApplication

    def get_query_information(self, query):
        late_duration = 0
        try:
            emp = EmployeeIdentification.objects.get(id=query)
            job = emp.employee_job_information.latest('updated_at') if emp.employee_job_information.exists() else ''
            information = {
                'name': emp,
                'designation': job.designation.name if job not in EMPTY_VALUES and
                job.designation not in EMPTY_VALUES else '',
                'employee_id': emp.employee_id,
                'schedule_type': emp.employee_attendance.last().schedule_type,
                'company': job.company.name if job not in EMPTY_VALUES and job.company not in EMPTY_VALUES else '',
                'division': job.division.name if job not in EMPTY_VALUES and job.division not in EMPTY_VALUES else '',
                'department': job.department.name if job not in EMPTY_VALUES and
                job.department not in EMPTY_VALUES else '',
                'business_unit': job.business_unit.name if job not in EMPTY_VALUES and
                job.business_unit not in EMPTY_VALUES else '',
                'project': job.project.name if job not in EMPTY_VALUES and job.project not in EMPTY_VALUES else ''
            }
            late_apply = LateApplication.objects.filter(attendance__employee_id=query)

            late_list = {
                'applied': late_apply.count(),
                'approved': late_apply.filter(status='approved').count(),
                'declined': late_apply.filter(status='declined').count(),
                'pending': late_apply.filter(status='pending').count(),
            }

            if late_apply:
                late_apply_day = late_apply.last().attendance
                timetable = TimeTable.objects.filter(schedule_master=emp.employee_attendance.last().schedule_type)
                em_deduction = LeaveManage.objects.filter(employee=emp)
                late_component = ''
                if em_deduction:
                    is_deduction = em_deduction[0].deduction
                    if is_deduction:
                        late_component = em_deduction[0].deduction_group.late_component
                if timetable:
                    for time_t in timetable:
                        if time_t.days.name == late_apply_day.date.strftime('%A'):
                            s_type = emp.employee_attendance.last().schedule_type.schedule_type
                            roster_type = emp.employee_attendance.last().schedule_type.roster_type
                            if late_component not in ['', None]:
                                late_duration = get_late_duration(s_type, time_t, late_apply_day, roster_type)
                                if late_duration != 0 and late_duration.seconds > 0:
                                    split_t = str(late_duration).split(':')
                                    late_duration = '{} hours, {} minutes'.format(split_t[0], split_t[1])
            return information, late_list, late_apply, late_duration
        except Exception as e:
            return e

    def get_instance(self):
        if self.kwargs.get('pk'):
            return get_object_or_404(LateApplication, Q(status__in=['approved', 'declined']), pk=self.kwargs['pk'])

    def get_late_information(self):
        late = self.get_instance()
        late_apply_day = late.attendance
        timetable = TimeTable.objects.filter(
            schedule_master=late.attendance.employee.employee_attendance.last().schedule_type)
        em_deduction = LeaveManage.objects.filter(employee=late.attendance.employee)
        late_component = ''
        if em_deduction:
            is_deduction = em_deduction[0].deduction
            if is_deduction:
                late_component = em_deduction[0].deduction_group.late_component

        data = {
            'created_at': late.created_at,
            'in_time': late.attendance.in_time,
            'date': late.attendance.date,
            'reason': late.reason_of_late,
            'attachment': late.attachment,
            'attachment_url': late.attachment.url if late.attachment not in EMPTY_VALUES else '',
            'status': late.get_status_display(),
        }
        if timetable:
            for time_t in timetable:
                if time_t.days.name == late_apply_day.date.strftime('%A'):
                    s_type = late.attendance.employee.employee_attendance.last().schedule_type.schedule_type
                    roster_type = late.attendance.employee.employee_attendance.last().schedule_type.roster_type
                    if late_component not in ['', None]:
                        late_duration = get_late_duration(s_type, time_t, late_apply_day, roster_type)
                        if late_duration != 0 and late_duration.seconds > 0:
                            split_t = str(late_duration).split(':')
                            late_duration = '{} hours, {} minutes'.format(split_t[0], split_t[1])
                        data['late_duration'] = late_duration
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

        context['employee'] = query
        if query is not None:
            info_qs = self.get_query_information(query)
            try:
                info, late_list, late_apply, late_duration = info_qs
                context['info'] = info
                context['late_list'] = late_list
                context['late_apply'] = late_apply
                context['late_duration'] = late_duration
                context['late_info'] = self.get_late_information()
                context['comment'] = LateApprovalComment.objects.filter(late_entry=self.kwargs['pk'])
            except TypeError:
                context['error'] = info_qs
        return context


class EntryTimeView(LoginRequiredMixin, PermissionMixin, TemplateView):
    """
        get time by ajax
    """

    def get(self, request, *args):
        query = request.GET.get('query')
        date = request.GET.get('date')
        attendance_time = AttendanceData.objects.filter(employee_id=query, date=date).last()
        if attendance_time:
            id = attendance_time.id
            temp = datetime.combine(attendance_time.date, attendance_time.in_time)
            in_time = datetime.strftime(temp, '%I:%M %p')
        else:
            id = None
            in_time = None
        data = {'attendance_id': id, 'in_time': in_time}
        return JsonResponse(data)


class LateIndividualListView(LoginRequiredMixin, PermissionMixin, ListView):

    """
        show individual employee late application list
        Access: Super-Admin, Admin
        Url: /admin/attendance/process/late_entry/list/?query=pk
    """
    template_name = 'attendance/process/late_entry/individual_list.html'
    model = LateApplication
    permission_required = 'view_lateapplication'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        object_list = []
        mylist = LateApplication.objects.filter(attendance__employee_id=self.kwargs['pk']).order_by('-updated_at')
        if mylist:
            emp = EmployeeIdentification.objects.get(id=self.kwargs['pk'])
            timetable = TimeTable.objects.filter(schedule_master=emp.employee_attendance.last().schedule_type)
            em_deduction = LeaveManage.objects.filter(employee=emp)
            late_component = ''
            if em_deduction:
                is_deduction = em_deduction[0].deduction
                if is_deduction:
                    late_component = em_deduction[0].deduction_group.late_component
            for late in mylist:
                data = {
                    'id': late.id,
                    'created': late.created_at,
                    'in_time': late.attendance.in_time,
                    'date': late.attendance.date,
                    'status': late.get_status_display(),
                    'employee_id': self.kwargs['pk'],
                }
                late_apply_day = late.attendance
                if timetable:
                    for time_t in timetable:
                        if time_t.days.name == late_apply_day.date.strftime('%A'):
                            s_type = emp.employee_attendance.last().schedule_type.schedule_type
                            roster_type = emp.employee_attendance.last().schedule_type.roster_type
                            if late_component not in ['', None]:
                                late_duration = get_late_duration(s_type, time_t, late_apply_day, roster_type)
                                if late_duration != 0 and late_duration.seconds > 0:
                                    split_t = str(late_duration).split(':')
                                    late_duration = '{} hours, {} minutes'.format(split_t[0], split_t[1])
                                data['late_duration'] = late_duration
                object_list.append(data)

        context['job'] = mylist.last().attendance.employee.employee_job_information.latest('updated_at')

        if object_list:
            paginator = Paginator(object_list, 50)
            page = self.request.GET.get('page')
            context['late_application'] = paginator.get_page(page)
            index = context['late_application'].number - 1
            max_index = len(paginator.page_range)
            start_index = index - 0 if index >= 3 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            context['page_range'] = list(paginator.page_range)[start_index:end_index]

        context['objects'] = object_list

        return context


class LatePendingListView(LoginRequiredMixin, PermissionMixin, ListView):
    """
        show pending late application list
        Access: Super-Admin, Admin
        Url: /admin/attendance/late_entry_approval/list/
    """
    template_name = 'attendance/process/late_approval/list.html'
    model = LateApplication
    permission_required = 'view_lateapplication'

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
            object_list = LateApplication.objects.filter(status='pending')
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
            mylist = LateApplication.objects.filter(status='pending').order_by('-updated_at')
        application_list = []
        if mylist:
            for late in mylist:
                late_apply_day = late.attendance
                timetable = TimeTable.objects.filter(
                    schedule_master=late.attendance.employee.employee_attendance.last().schedule_type)
                em_deduction = LeaveManage.objects.filter(employee=late.attendance.employee)
                late_component = ''
                if em_deduction:
                    is_deduction = em_deduction[0].deduction
                    if is_deduction:
                        late_component = em_deduction[0].deduction_group.late_component

                data = {
                    'id': late.id,
                    'created_at': late.created_at,
                    'in_time': late.attendance.in_time,
                    'date': late.attendance.date,
                    'status': late.get_status_display(),
                    'employee_id': late.attendance.employee.id,
                    'name': late.attendance.employee,
                    'designation': late.attendance.employee.employee_job_information.latest('updated_at'),
                }
                if timetable:
                    for time_t in timetable:
                        if time_t.days.name == late_apply_day.date.strftime('%A'):
                            s_type = late.attendance.employee.employee_attendance.last().schedule_type.schedule_type
                            roster_type = late.attendance.employee.employee_attendance.last().schedule_type.roster_type
                            if late_component not in ['', None]:
                                try:
                                    late_duration = get_late_duration(s_type, time_t, late_apply_day, roster_type)
                                    if late_duration != 0 and late_duration.seconds > 0:
                                        split_t = str(late_duration).split(':')
                                        late_duration = '{} hours, {} minutes'.format(split_t[0], split_t[1])
                                    data['late_duration'] = late_duration
                                except:
                                    pass
                application_list.append(data)

        if application_list:
            paginator = Paginator(application_list, 50)
            page = self.request.GET.get('page')
            context['pending_application'] = paginator.get_page(page)
            index = context['pending_application'].number - 1
            max_index = len(paginator.page_range)
            start_index = index - 0 if index >= 3 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            context['page_range'] = list(paginator.page_range)[start_index:end_index]
            context['path'] = "%s" % "&".join(["%s=%s" % (key, value) for (key, value) in self.request.GET.items()
                                               if not key == 'page'])

        context['objects'] = application_list

        return context


class LateApprovalView(LoginRequiredMixin, PermissionMixin, TemplateView):
    """
        Late late_approval form
        Access: Super-Admin, Admin
        Url: /admin/attendance/process/late_entry_approval/<pk>/
    """
    template_name = 'attendance/process/late_approval/create.html'
    permission_required = 'change_lateapplication'

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

    def get_late_information(self):
        late = self.get_instance()
        late_apply_day = late.attendance
        timetable = TimeTable.objects.filter(
            schedule_master=late.attendance.employee.employee_attendance.last().schedule_type)
        em_deduction = LeaveManage.objects.filter(employee=late.attendance.employee)
        late_component = ''
        if em_deduction:
            is_deduction = em_deduction[0].deduction
            if is_deduction:
                late_component = em_deduction[0].deduction_group.late_component

        data = {
            'created_at': late.created_at,
            'in_time': late.attendance.in_time,
            'date': late.attendance.date,
            'reason': late.reason_of_late,
            'attachment': late.attachment,
            'attachment_url': late.attachment.url if late.attachment not in EMPTY_VALUES else '',
        }
        if timetable:
            for time_t in timetable:
                if time_t.days.name == late_apply_day.date.strftime('%A'):
                    s_type = late.attendance.employee.employee_attendance.last().schedule_type.schedule_type
                    roster_type = late.attendance.employee.employee_attendance.last().schedule_type.roster_type
                    if late_component not in ['', None]:
                        late_duration = get_late_duration(s_type, time_t, late_apply_day, roster_type)
                        if late_duration != 0 and late_duration.seconds > 0:
                            split_t = str(late_duration).split(':')
                            late_duration = '{} hours, {} minutes'.format(split_t[0], split_t[1])
                        data['late_duration'] = late_duration
        return data

    def get_instance(self):
        return get_object_or_404(LateApplication, Q(status='pending'), pk=self.kwargs['pk'])

    def get_comment(self):
        return LateApprovalComment.objects.filter(late_entry=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        entry = self.kwargs.get('pk')
        if entry is not None:
            context['employee_info'] = self.get_employee_information()
            context['late_info'] = self.get_late_information()
            context['form'] = LateApprovalForm()
            context['comment'] = self.get_comment()
        return context

    def post(self, request, *args, **kwargs):
        context = dict()
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        entry = self.kwargs.get('pk')
        if entry is not None:
            context['employee_info'] = self.get_employee_information()
            context['late_info'] = self.get_late_information()
            context['form'] = LateApprovalForm(request.POST)
            context['comment'] = self.get_comment()

        if 'save_comment' in request.POST:
            form = LateApprovalForm(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                form.user = request.user
                form.late_entry_id = entry
                form.save()
                return redirect('beehive_admin:attendance:late_approval_form', entry)
        if 'decline' in request.POST:
            approval = Approval(request)
            approval.approve_or_decline('declined', 'late-entry', entry)

            approvals = ApprovalModel.objects.filter(
                item=entry,
                item_type='late-entry'
            )
            declined_approvals = list(filter(lambda approval: approval.status == 'declined', approvals))

            if approvals.count() == len(declined_approvals):
                LateApplication.objects.filter(id=entry).update(status='declined')
                approval.set_notifications(
                    notification_for=entry,
                    content='Late entry declined'
                )

            return redirect('beehive_admin:attendance:late_entry_application_list')
        if 'approve' in request.POST:
            approval = Approval(request)
            approval.approve_or_decline('approved', 'late-entry', entry)

            approvals = ApprovalModel.objects.filter(
                item=entry,
                item_type='late-entry'
            )
            appvoed_approvals = list(filter(lambda approval: approval.status == 'approved', approvals))

            if approvals.count() == len(appvoed_approvals):
                leave_approve = LateApplication.objects.filter(id=entry)
                leave_approve.update(status='approved')
                daily_record = DailyRecord.objects.filter(schedule_record__employee=leave_approve[0].attendance.employee,
                                                          schedule_record__date=leave_approve[0].attendance.date)

                approval.set_notifications(
                    notification_for=entry,
                    content='Late entry approved'
                )

                if daily_record.exists():
                    early_out = daily_record[0].early
                    late = False
                    if late or early_out:
                        under_work = True
                    else:
                        under_work = False
                    daily_record.update(late=late, is_present=True, under_work=under_work)

            return redirect('beehive_admin:attendance:late_entry_application_list')

        return render(request, self.template_name, context)

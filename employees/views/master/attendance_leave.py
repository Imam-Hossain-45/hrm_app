from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from employees.forms import LeaveManageForm, AttendanceManageForm
from employees import models as emp_models
from django.shortcuts import render, redirect, get_object_or_404
from helpers.mixins import PermissionMixin
from django.contrib import messages
from leave.models import LeaveGroupSettings, LeaveGroup, LeaveAvail, LeaveRemaining
from datetime import datetime, timedelta
from attendance.models import HolidayMaster, DailyRecord, ScheduleRecord, TimeTableRecord, BreakTimeRecord
from django.db.models import Q
from leave.views.process import convert_time_unit_into_seconds
from leave.views.master import set_leave_remaining
from helpers.functions import get_organizational_structure


class LeaveManagerCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Assign an employee in a leave group
        Access: Super-Admin, Admin
        Url: /employee/<pk>/attendance_&_leave
    """
    form_class = LeaveManageForm
    second_form_class = AttendanceManageForm
    template_name = 'employees/master/attendance_&_leave/create.html'
    permission_required = ['add_leavemanage', 'change_leavemanage', 'view_leavemanage',
                           'delete_leavemanage']

    def get_queryset(self):
        if self.get_leave_information() and self.get_leave_information().leave_group is not None:
            leave_list = []
            for leave in self.get_leave_information().leave_group.leave.all():
                try:
                    leave_settings = LeaveGroupSettings.objects.get(leave_name=leave,
                                                                    leave_group=self.get_leave_information().leave_group)
                    leave_credit = str(
                        leave_settings.leave_credit) + ' ' + leave.time_unit_basis
                except:
                    leave_credit = ''
                data = {
                    'leave_name': leave.name,
                    'credit_period': str(leave.available_frequency_number) + ' ' + leave.available_frequency_unit,
                    'leave_credit': leave_credit
                }
                leave_list.append(data)
            return leave_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification,
                          pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']
        context['leave_list'] = self.get_queryset()
        if 'attendance_form' not in context:
            if self.get_attendance_information():
                context['attendance_form'] = self.second_form_class(
                    instance=self.get_attendance_information())
            else:
                context['attendance_form'] = self.second_form_class()
        if 'leave_form' not in context:
            if self.get_leave_information():
                context['leave_form'] = self.form_class(
                    instance=self.get_leave_information())
            else:
                context['leave_form'] = self.form_class()
        return context

    def get_leave_information(self):
        leave = emp_models.LeaveManage.objects.filter(
            employee_id=self.kwargs['pk']).first()
        return leave

    def get_attendance_information(self):
        attendance = emp_models.Attendance.objects.filter(
            employee_id=self.kwargs['pk']).first()
        return attendance

    def post(self, request, *args, **kwargs):
        context = dict()
        get_object = get_object_or_404(
            emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        if 'attendance_form' not in context:
            attendance_info = self.get_attendance_information()
            if attendance_info:
                context['attendance_form'] = self.second_form_class(
                    instance=attendance_info)
            else:
                context['attendance_form'] = self.second_form_class()
        if 'leave_form' not in context:
            leave_info = self.get_leave_information()
            if leave_info:
                context['leave_form'] = self.form_class(instance=leave_info)
            else:
                context['leave_form'] = self.form_class()
        context['pk'] = self.kwargs['pk']
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['leave_list'] = self.get_queryset()

        if 'form1' in request.POST:
            context['attendance_form'] = self.second_form_class(request.POST)
            attendance_form = context['attendance_form']
            if attendance_form.is_valid():
                obj, created = emp_models.Attendance.objects.update_or_create(employee_id=self.kwargs['pk'], defaults={
                    'schedule_type': attendance_form.cleaned_data['schedule_type'],
                    'punching_id': attendance_form.cleaned_data['punching_id'],
                    'calendar_master': attendance_form.cleaned_data['calendar_master']})

                # self.set_daily_record(self.kwargs['pk'], attendance_form.cleaned_data['schedule_type'],
                #                       attendance_form.cleaned_data['calendar_master'])

                if created:
                    messages.success(self.request, "Created.")
                else:
                    messages.success(self.request, "Updated")
                return redirect('employees:employee_attendance_leave', self.kwargs['pk'])

        if 'form2' in request.POST:
            leave_info = self.get_leave_information()
            context['leave_form'] = self.form_class(
                request.POST, instance=leave_info)
            leave_form = context['leave_form']
            if leave_form.is_valid():
                l_group = leave_form.cleaned_data.get('leave_group')
                leave_remaining_qs = LeaveRemaining.objects
                if l_group not in ['', None]:
                    leavegroup = LeaveGroup.objects.get(
                        name=leave_form.cleaned_data['leave_group'])
                    for l in leavegroup.leave.all():
                        if l.gender != 'all' and l.gender != get_object.gender:
                            messages.error(
                                self.request, l.name + " is only for " + l.gender + " employees.")
                            return render(request, self.template_name, context)
                    leave_remaining_list = []
                    for l in leavegroup.leave.all():
                        leave_remaining_obj = leave_remaining_qs.filter(employee_id=self.kwargs['pk'], leave=l,
                                                                        status=True)
                        total_remain, total_avail_leave = set_leave_remaining(
                            self.kwargs['pk'], l, l_group.id)

                        try:
                            in_seconds = convert_time_unit_into_seconds(
                                l, total_remain)
                            total_avail_leave_in_seconds = convert_time_unit_into_seconds(
                                l, total_avail_leave)
                            # if this leave already has update this leave row otherwise create a row for this leave
                            if leave_remaining_obj:
                                leave_remaining_obj.update(remaining_in_seconds=in_seconds,
                                                           availing_in_seconds=total_avail_leave_in_seconds)
                                leave_remaining_list.append(
                                    leave_remaining_obj[0].id)
                            else:
                                leave_remain = leave_remaining_qs.\
                                    create(employee_id=self.kwargs['pk'], leave=l,
                                           status=True,
                                           remaining_in_seconds=in_seconds,
                                           availing_in_seconds=total_avail_leave_in_seconds)
                                leave_remaining_list.append(leave_remain.id)
                        except TypeError:
                            # error of django : 'NoneType' object has no attribute 'date_of_joining'
                            messages.error(
                                self.request, "Please add job information for this employee.")
                            return render(request, self.template_name, context)

                    # after update or create leave remaining row another row those status True will be false,
                    # because the employee will not get the leave
                    leave_remaining_qs.exclude(id__in=leave_remaining_list). \
                        filter(
                            employee_id=self.kwargs['pk'], status=True).delete()
                    # update(status=False, leave_avail_date=datetime.now())
                else:
                    # if no leave group assign before remaining leave those status true are deleted
                    leave_remaining_qs.filter(
                        employee_id=self.kwargs['pk'], status=True).delete()

                obj, created = emp_models.LeaveManage.objects.update_or_create(employee_id=self.kwargs['pk'], defaults={
                    'leave_group': l_group,
                    'overtime': leave_form.cleaned_data['overtime'],
                    'overtime_group': leave_form.cleaned_data['overtime_group'],
                    'deduction': leave_form.cleaned_data['deduction'],
                    'deduction_group': leave_form.cleaned_data['deduction_group']})

                if created:
                    messages.success(self.request, "Created.")
                else:
                    messages.success(self.request, "Updated")
                return redirect('employees:employee_attendance_leave', self.kwargs['pk'])

        return render(request, self.template_name, context)

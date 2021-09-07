from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.validators import EMPTY_VALUES
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, FormView, DeleteView

from attendance.forms import EarlyOutForm, EarlyApprovalForm
from attendance.models import TimeTable, EarlyApplication, EarlyApprovalComment
from attendance.views import get_duration
from employees.models import LeaveManage
from helpers.functions import get_organizational_structure
from helpers.mixins import PermissionMixin
from user_management.workflow import Approval


class EarlyOutStatusListView(LoginRequiredMixin, UserPassesTestMixin, PermissionMixin, ListView):
    """Early out status view."""

    template_name = 'self_panel/early-out/list.html'
    model = EarlyApplication
    context_object_name = 'applications'

    def test_func(self):
        return self.request.user.self_panel and self.request.user.employee

    def get_queryset(self):
        query_filter = {
            'attendance__employee': self.request.user.employee
        }

        if 'from_date' in self.request.GET and self.request.GET['from_date'] is not '':
            query_filter['attendance__date__gte'] = self.request.GET['from_date']

        if 'to_date' in self.request.GET and self.request.GET['to_date'] is not '':
            query_filter['attendance__date__lte'] = self.request.GET['to_date']

        return self.model.objects.filter(**query_filter)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        return context


class EarlyOutApplyView(LoginRequiredMixin, UserPassesTestMixin, PermissionMixin, CreateView):
    """Apply for a early out entry."""

    template_name = 'self_panel/early-out/apply.html'
    form_class = EarlyOutForm
    success_url = reverse_lazy('self_panel:late_status')

    def test_func(self):
        return self.request.user.self_panel and self.request.user.employee

    def get_last_apply_information(self):
        data = {}
        emp = self.request.user.employee
        early_apply = EarlyApplication.objects.filter(attendance__employee_id=emp.id)
        last_apply = early_apply.last()
        out_time = last_apply.early_out_time

        if last_apply and last_apply is not None:
            early_out_component = ''
            early_apply_day = last_apply.attendance
            timetable = TimeTable.objects.filter(schedule_master=emp.employee_attendance.last().schedule_type)
            em_deduction = LeaveManage.objects.filter(employee_id=emp)

            if last_apply.attendance.out_time is not None:
                out_time = last_apply.attendance.out_time

            data = {
                'date': last_apply.attendance.date,
                'in_time': last_apply.attendance.in_time,
                'out_date': last_apply.attendance.out_date
                if last_apply.attendance.out_date not in EMPTY_VALUES else last_apply.attendance.date,
                'out_time': out_time,
                'status': last_apply.status,
                'get_status_display': last_apply.get_status_display(),
            }

            if em_deduction and em_deduction[0].deduction:
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
                                    data['duration'] = '{} hours, {} minutes'.format(split_t[0], split_t[1])

        return data

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs()
        kwargs['query'] = self.request.user.employee_id

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['employee'] = self.request.user.employee_id
        context['last_applied_data'] = self.get_last_apply_information()

        return context

    def form_valid(self, form):
        model = form.save(commit=False)
        model.attendance_id = form.cleaned_data['attendance']
        model.reason_of_early_out = form.cleaned_data['reason_of_early_out']
        model.early_out_time = form.cleaned_data['early_out_time']
        model.status = 'pending'
        model.save()

        Approval(request=self.request, model=form, item_type='early-out').set()

        return super().form_valid(form)


class EarlyOutUpdateView(LoginRequiredMixin, UserPassesTestMixin, PermissionMixin, FormView):
    """Comment system on early out."""

    template_name = 'self_panel/early-out/edit.html'
    form_class = EarlyApprovalForm

    def test_func(self):
        return self.request.user.self_panel and self.request.user.employee

    def get_early_information(self):
        early = get_object_or_404(EarlyApplication, pk=self.kwargs['pk'], attendance__employee=self.request.user.employee)
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
            'date': early.attendance.date,
            'created_at': early.created_at,
            'out_time': out_time,
            'out_date': early.attendance.out_date
            if early.attendance.out_date not in EMPTY_VALUES else early.attendance.date,
            'reason': early.reason_of_early_out,
            'attachment': early.attachment,
            'attachment_url': early.attachment.url if early.attachment not in EMPTY_VALUES else '',
            'status': early.status,
            'get_status_display': early.get_status_display()
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

    def get_comment(self):
        return EarlyApprovalComment.objects.filter(early_out=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['early_info'] = self.get_early_information()
        context['comments'] = self.get_comment()
        context['pk'] = self.kwargs['pk']

        return context

    def form_valid(self, form):
        model = form.save(commit=False)
        model.user = self.request.user
        model.early_out_id = self.kwargs['pk']
        model.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('self_panel:early_out_update', kwargs={
            'pk': self.kwargs['pk']
        })


class EarlyOutDeleteView(LoginRequiredMixin, UserPassesTestMixin, PermissionMixin, DeleteView):
    """Early out delete view."""

    model = EarlyApplication
    success_url = reverse_lazy('self_panel:early_out_status')

    def test_func(self):
        return self.request.user.self_panel and self.request.user.employee

    def get_object(self):
        return get_object_or_404(
            EarlyApplication,
            pk=self.kwargs['pk'],
            status='pending',
            attendance__employee=self.request.user.employee
        )

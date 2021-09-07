from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.validators import EMPTY_VALUES
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, FormView, DeleteView

from attendance.forms import LateEntryForm, LateApprovalForm
from attendance.models import LateApplication, LateApprovalComment, TimeTable
from attendance.views import get_late_duration
from employees.models import LeaveManage
from helpers.functions import get_organizational_structure
from helpers.mixins import PermissionMixin
from user_management.workflow import Approval


class LateStatusListView(LoginRequiredMixin, UserPassesTestMixin, PermissionMixin, ListView):
    """Late status view."""

    template_name = 'self_panel/late/list.html'
    model = LateApplication
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


class LateApplyView(LoginRequiredMixin, UserPassesTestMixin, PermissionMixin, CreateView):
    """Apply for a late entry."""

    template_name = 'self_panel/late/apply.html'
    form_class = LateEntryForm
    success_url = reverse_lazy('self_panel:late_status')

    def test_func(self):
        return self.request.user.self_panel and self.request.user.employee

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['employee'] = self.request.user.employee_id

        return context

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs()
        kwargs['query'] = self.request.user.employee_id

        return kwargs

    def form_valid(self, form):
        model = form.save(commit=False)
        model.attendance_id = form.cleaned_data['attendance']
        model.reason_of_late = form.cleaned_data['reason_of_late']
        model.save()

        Approval(request=self.request, model=model, item_type='late-entry').set()

        return super().form_valid(form)


class LateUpdateView(LoginRequiredMixin, UserPassesTestMixin, PermissionMixin, FormView):
    """Comment system on late."""

    template_name = 'self_panel/late/edit.html'
    form_class = LateApprovalForm

    def test_func(self):
        return self.request.user.self_panel and self.request.user.employee

    def get_late_information(self):
        late_component = ''
        late = get_object_or_404(
            LateApplication, pk=self.kwargs['pk'], attendance__employee=self.request.user.employee)
        late_apply_day = late.attendance
        timetable = TimeTable.objects.filter(
            schedule_master=late.attendance.employee.employee_attendance.last().schedule_type)
        em_deduction = LeaveManage.objects.filter(
            employee=self.request.user.employee)

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
            'status': late.status,
            'get_status_display': late.get_status_display(),
        }

        if timetable:
            for time_t in timetable:
                if time_t.days.name == late_apply_day.date.strftime('%A'):
                    s_type = late.attendance.employee.employee_attendance.last().schedule_type.schedule_type
                    roster_type = late.attendance.employee.employee_attendance.last().schedule_type.roster_type

                    if late_component not in ['', None]:
                        late_duration = get_late_duration(
                            s_type, time_t, late_apply_day, roster_type)

                        if late_duration != 0 and late_duration.seconds > 0:
                            split_t = str(late_duration).split(':')
                            late_duration = '{} hours, {} minutes'.format(
                                split_t[0], split_t[1])

                        data['late_duration'] = late_duration
        return data

    def get_comment(self):
        return LateApprovalComment.objects.filter(late_entry=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['late_info'] = self.get_late_information()
        context['comments'] = self.get_comment()
        context['pk'] = self.kwargs['pk']

        return context

    def form_valid(self, form):
        model = form.save(commit=False)
        model.user = self.request.user
        model.late_entry_id = self.kwargs['pk']
        model.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('self_panel:late_update', kwargs={
            'pk': self.kwargs['pk']
        })


class LateDeleteView(LoginRequiredMixin, UserPassesTestMixin, PermissionMixin, DeleteView):
    """Late delete view."""

    model = LateApplication
    success_url = reverse_lazy('self_panel:late_status')

    def test_func(self):
        return self.request.user.self_panel and self.request.user.employee

    def get_object(self):
        return get_object_or_404(LateApplication, pk=self.kwargs['pk'], attendance__employee=self.request.user.employee)

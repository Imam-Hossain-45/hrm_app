from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView, FormView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate, logout as auth_logout
from .forms import LogInForm
from helpers.mixins import PermissionMixin
from helpers.functions import get_organizational_structure
from attendance.models.process.attendance_entry import DailyRecord
from datetime import datetime
from leave.models import LeaveMaster, LeaveEntry, LeaveAvail, LeaveRemaining
from leave.views.process import set_daily_record, get_remaining_leave, get_minimum_gap, get_restriction


class IndexView(LoginRequiredMixin, PermissionMixin, TemplateView):
    """
    Main index view.
    Url: /
    """

    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['on_time_employee'] = DailyRecord.objects.filter(is_present=True, late=False,
                                                                 schedule_record__date=datetime.today())
        context['late_employee'] = DailyRecord.objects.filter(is_present=True, late=True,
                                                              schedule_record__date=datetime.today())
        context['absent_employee'] = DailyRecord.objects.filter(is_present=False, schedule_record__is_working_day=True,
                                                                schedule_record__is_leave=False,
                                                                schedule_record__date=datetime.today())

        context['leave_master'] = LeaveMaster.objects.filter(status=True)
        context['all_pending_leave'] = LeaveEntry.objects.filter(status='pending', leave_type__status=True)
        return context

    # def post(self, request, *args, **kwargs):
    #     if 'decline_btn' in request.POST:
    #         LeaveEntry.objects.filter(id=request.POST['leave_entry_id']).update(status='declined')
    #         messages.error(self.request, "Declined a leave application.")
    #     else:
    #         leave_entry_qs = LeaveEntry.objects.filter(id=request.POST['leave_entry_id'])
    #
    #         # validation for remaining leave
    #         td_start = leave_entry_qs[0].start_time
    #         if td_start is not None:
    #             split_start_time = str(td_start).split(":")
    #             start_time = split_start_time[0] + ":" + split_start_time[1]
    #         else:
    #             start_time = None
    #         td_end = leave_entry_qs[0].end_time
    #         if td_end is not None:
    #             split_end_time = str(td_end).split(":")
    #             end_time = split_end_time[0] + ":" + split_end_time[1]
    #         else:
    #             end_time = None
    #         end_time, availing, remain_leave, total_avail, msg = get_remaining_leave(
    #                                                              leave_entry_qs[0].employee.id,
    #                                                              leave_entry_qs[0].leave_type.id,
    #                                                              leave_entry_qs[0].start_date,
    #                                                              leave_entry_qs[0].end_date,
    #                                                              start_time, end_time,
    #                                                              leave_entry_qs[0].leave_type.sandwich_leave_allowed
    #                                                             )
    #         if request.user.is_superuser or request.user.management:
    #             remaining_data = True
    #         else:
    #             if msg is '':
    #                 remaining_data = True
    #             else:
    #                 remaining_data = False
    #                 messages.error(self.request, msg)
    #
    #         # validation for minimum gap
    #         if request.user.is_superuser or request.user.management:
    #             gap_data = True
    #         else:
    #             gap = get_minimum_gap(leave_entry_qs[0].employee.id, leave_entry_qs[0].leave_type.id,
    #                                   leave_entry_qs[0].start_date, leave_entry_qs[0].end_date)
    #             if gap is '':
    #                 gap_data = True
    #             else:
    #                 gap_data = False
    #                 messages.error(self.request, gap)
    #
    #         # validation for restriction
    #         if request.user.is_superuser or request.user.management:
    #             restriction_data = True
    #         else:
    #             restriction = get_restriction(leave_entry_qs[0].employee.id, leave_entry_qs[0].leave_type.id,
    #                                           leave_entry_qs[0].start_date,
    #                                           leave_entry_qs[0].end_date, start_time,
    #                                           end_time, leave_entry_qs[0].leave_type.sandwich_leave_allowed)
    #             if restriction is '':
    #                 restriction_data = True
    #             else:
    #                 restriction_data = False
    #                 messages.error(self.request, restriction)
    #
    #         if remaining_data is True and gap_data is True and restriction_data is True:
    #             LeaveAvail.objects.create(employee=leave_entry_qs[0].employee,
    #                                       avail_leave=leave_entry_qs[0].leave_type,
    #                                       credit_seconds=availing,
    #                                       start_date=leave_entry_qs[0].start_date,
    #                                       end_date=leave_entry_qs[0].end_date,
    #                                       start_time=leave_entry_qs[0].start_time,
    #                                       end_time=leave_entry_qs[0].end_time,
    #                                       notes='Approved this leave')
    #
    #             LeaveRemaining.objects.update_or_create(employee=leave_entry_qs[0].employee,
    #                                                     leave_id=leave_entry_qs[0].leave_type,
    #                                                     status=True,
    #                                                     defaults={
    #                                                         'remaining_in_seconds': remain_leave,
    #                                                         'availing_in_seconds': total_avail
    #                                                     })
    #
    #             leave_entry_qs.update(status='approved')
    #             set_daily_record(leave_entry_qs[0].employee.id, leave_entry_qs[0].start_date,
    #                              leave_entry_qs[0].end_date, leave_entry_qs[0].leave_type.paid, leave_entry_qs[0].leave_type,
    #                              availing, leave_entry_qs[0].leave_type.sandwich_leave_allowed)
    #             messages.success(self.request, "Accept a leave application.")
    #         # else:
    #         #     messages.error(self.request, "Cannot accept this leave application.")
    #     return redirect('index')


class LogInView(FormView):
    """
    Show a login form to log a user in.

    Url: /accounts/login/
    """
    form_class = LogInForm
    template_name = 'accounts/logIn.html'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        user = authenticate(username=email, password=password)

        if user is None:
            messages.error(self.request, 'Sorry, we did not find any matching user with the provided credentials')

            return redirect(reverse_lazy('accounts:login'))

        if user.is_active:
            login(self.request, user)
            if 'next' in self.request.POST:
                return redirect(self.request.POST.get('next'))
            else:
                return redirect(reverse_lazy('index'))

        messages.error(self.request, 'The user is inactive. Please contact with administrator')

        return redirect(reverse_lazy('accounts:login'))


class LogOutView(LoginRequiredMixin, RedirectView):
    """
    Log a user out.

    Url: /accounts/logout/
    """

    def get_redirect_url(self, *args, **kwargs):
        auth_logout(self.request)

        return reverse_lazy('accounts:login')

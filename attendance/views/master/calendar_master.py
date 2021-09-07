from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, DeleteView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from attendance.models import CalendarMaster
from django.conf import settings
from helpers.mixins import PermissionMixin
from attendance.forms import CalendarForm
from django.core.validators import EMPTY_VALUES
from django.shortcuts import render
from datetime import timedelta
from helpers.functions import get_organizational_structure


class ListCalendarMasterView(LoginRequiredMixin, PermissionMixin, ListView):
    """List of Calendar Master"""

    template_name = "attendance/master/calendar/list.html"
    model = CalendarMaster
    permission_required = ['add_calendarmaster', 'change_calendarmaster', 'view_calendarmaster',
                           'delete_calendarmaster']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        paginator = Paginator(self.object_list, 50)
        page = self.request.GET.get('page')
        context['calendar_list'] = paginator.get_page(page)
        index = context['calendar_list'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class AddCalendarMasterView(LoginRequiredMixin, PermissionMixin, CreateView):
    """Create new calendar_master"""

    template_name = 'attendance/master/calendar/create.html'
    permission_required = 'add_calendarmaster'
    form_class = CalendarForm
    success_url = reverse_lazy('beehive_admin:attendance:master_calendar_list')

    def render_to_response(self, context, **response_kwargs):
        """ Allow AJAX requests to be handled more gracefully """
        if self.request.is_ajax():
            parent_id = self.request.GET.get('parent_id')
            if parent_id not in EMPTY_VALUES:
                form = self.form_class(instance=CalendarMaster.objects.filter(id=parent_id).first())
            else:
                form = self.form_class()
            return render(self.request, 'attendance/master/calendar/parent_form.html',
                          {'form': form, 'permissions': self.get_current_user_permission_list(),
                           'org_items_list': get_organizational_structure()
                           })
        else:
            return super(CreateView, self).render_to_response(context, **response_kwargs)

    def form_valid(self, form):
        effective_start_date = form.instance.effective_start_date
        effective_end_date = form.instance.effective_end_date
        if effective_end_date in EMPTY_VALUES:
            form.instance.effective_end_date = effective_start_date + timedelta(days=365*3)
        return super(AddCalendarMasterView, self).form_valid(form)


class EditCalendarMasterView(LoginRequiredMixin, PermissionMixin, SuccessMessageMixin, UpdateView):
    """
        Change CalendarMaster
    """
    form_class = CalendarForm
    success_message = "Updated Successfully"
    template_name = "attendance/master/calendar/update.html"
    success_url = reverse_lazy("beehive_admin:attendance:master_calendar_list")
    permission_required = 'change_calendarmaster'

    def get_queryset(self):
        return CalendarMaster.objects.filter(id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def render_to_response(self, context, **response_kwargs):
        """ Allow AJAX requests to be handled more gracefully """
        if self.request.is_ajax():
            parent_id = self.request.GET.get('parent_id')

            if parent_id not in EMPTY_VALUES:
                form = self.form_class(instance=CalendarMaster.objects.filter(id=parent_id).first())
            else:
                form = self.form_class()
            return render(self.request, 'attendance/master/calendar/parent_form.html',
                          {'form': form, 'permissions': self.get_current_user_permission_list(),
                           'org_items_list': get_organizational_structure()
                           })
        else:
            return super(UpdateView, self).render_to_response(context, **response_kwargs)

    def form_valid(self, form):
        effective_start_date = form.instance.effective_start_date
        effective_end_date = form.instance.effective_end_date
        if effective_end_date in EMPTY_VALUES:
            form.instance.effective_end_date = effective_start_date + timedelta(days=365*3)
        return super(EditCalendarMasterView, self).form_valid(form)


class DeleteCalendarMasterView(LoginRequiredMixin, PermissionMixin, SuccessMessageMixin, DeleteView):
    """
        Delete calendar_master
    """
    login_url = settings.LOGIN_URL
    model = CalendarMaster
    success_message = "%(name)s deleted."
    success_url = reverse_lazy("beehive_admin:attendance:master_calendar_list")
    permission_required = 'delete_calendarmaster'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(DeleteCalendarMasterView, self).delete(request, *args, **kwargs)

from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, DeleteView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from attendance.forms import HolidayMasterCreateForm
from attendance.models import HolidayMaster
from helpers.mixins import PermissionMixin
from helpers.functions import get_organizational_structure


class HolidayMasterList(LoginRequiredMixin, PermissionMixin, ListView):
    """
        List of Holiday Master
    """

    model = HolidayMaster
    template_name = "attendance/master/holiday_master/list.html"
    permission_required = ['add_holidaymaster', 'change_holidaymaster', 'view_holidaymaster', 'delete_holidaymaster']

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        paginator = Paginator(self.object_list, 50)
        page = self.request.GET.get('page')
        context['holidays'] = paginator.get_page(page)
        index = context['holidays'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class HolidayMasterCreate(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Create new Holiday Master
    """

    template_name = 'attendance/master/holiday_master/create.html'
    permission_required = 'add_holidaymaster'

    def get(self, request, *args, **kwargs):
        context = {'form': HolidayMasterCreateForm(), 'permissions': self.get_current_user_permission_list(),
                   'org_items_list': get_organizational_structure()}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = HolidayMasterCreateForm(request.POST)

        if form.is_valid():
            obj_holiday_master = form.save(commit=False)
            obj_holiday_master.save()
            messages.success(request, f'{obj_holiday_master} was created successfully')
            return redirect(reverse_lazy('beehive_admin:attendance:holiday_master_list'))

        return render(request, self.template_name, {'form': form,
                                                    'permissions': self.get_current_user_permission_list(),
                                                    'org_items_list': get_organizational_structure()})


class HolidayMasterUpdate(LoginRequiredMixin, PermissionMixin, SuccessMessageMixin, UpdateView):
    """
        Change Holiday Master
    """

    model = HolidayMaster
    form_class = HolidayMasterCreateForm
    success_message = "Updated Successfully"
    template_name = "attendance/master/holiday_master/update.html"
    success_url = reverse_lazy("beehive_admin:attendance:holiday_master_list")
    permission_required = 'change_holidaymaster'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context


class HolidayMasterDelete(LoginRequiredMixin, PermissionMixin, SuccessMessageMixin, DeleteView):
    """
        Delete holiday_master
    """

    model = HolidayMaster
    template_name = "attendance/master/holiday_master/delete.html"
    success_message = "%(name)s deleted."
    success_url = reverse_lazy("beehive_admin:attendance:holiday_master_list")
    permission_required = 'delete_holidaymaster'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(HolidayMasterDelete, self).delete(request, *args, **kwargs)

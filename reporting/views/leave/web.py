from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from helpers.mixins import PermissionMixin
from reporting.forms import EmployeeFilterForm
from helpers.functions import get_organizational_structure


class LeaveReportView(LoginRequiredMixin, PermissionMixin, TemplateView):
    template_name = 'reporting/leave/index.html'
    permission_required = ['view_leaveentry', 'view_leaveavail', 'view_leaveremaining']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context.setdefault('employee_filter_form', EmployeeFilterForm())
        return context

    def get(self, request, *args, **kwargs):
        if 'employee-filter-in-effect' in request.GET:
            print(1)
            context_kwargs = {}
            employee_filter_form = EmployeeFilterForm(request.GET)
            if employee_filter_form.is_valid():
                print(2)
                context_kwargs['report_view_from_date'] = employee_filter_form.cleaned_data.get('from_date')
                context_kwargs['report_view_to_date'] = employee_filter_form.cleaned_data.get('to_date')
                employee_list = employee_filter_form.cleaned_data.get('employees')
                if employee_list:
                    context_kwargs['report_view_type'] = 'employee_wise'
                    context_kwargs['report_employee'] = employee_list[0]
                else:
                    context_kwargs['report_view_type'] = 'consolidated'
            else:
                print(3)
                context_kwargs['employee_filter_form'] = employee_filter_form
            context = self.get_context_data(**context_kwargs)
            return self.render_to_response(context)
        else:
            return super().get(request, *args, **kwargs)

import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from helpers.functions import get_employee_query_info
from helpers.mixins import PermissionMixin
from leave.forms import SearchForm
from django.core.validators import EMPTY_VALUES


class PaySuggestionsReportView(LoginRequiredMixin, PermissionMixin, TemplateView):
    template_name = 'payroll/report/pay_suggestions.html'
    permission_required = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = ''

        context['permissions'] = self.get_current_user_permission_list()
        context['report_url'] = os.environ['REPORT_URL']
        form = SearchForm()
        if self.request.GET:
            form = SearchForm(self.request.GET)
            from_date = self.request.GET.get('from_date')
            to_date = self.request.GET.get('to_date')
            company = self.request.GET.get('company') or 'ALL'
            context['division'] = self.request.GET.get('division') or 'ALL'
            context['department'] = self.request.GET.get('department') or 'ALL'
            context['business_unit'] = self.request.GET.get('business_unit') or 'ALL'
            context['branch'] = self.request.GET.get('branch') or 'ALL'
            context['schedule'] = self.request.GET.get('schedule') or 'ALL'

            if self.request.GET.get('query'):
                employee = self.request.GET.get('employee')

            if employee:
                context['employee'] = get_employee_query_info(employee)

            if from_date in EMPTY_VALUES:
                form.add_error('from_date', 'This field is required')

            if to_date in EMPTY_VALUES:
                form.add_error('to_date', 'This field is required')

            if employee in EMPTY_VALUES and company in [None, '', 'ALL']:
                form.add_error('company', 'Select a company name')

            context['from_date'] = from_date
            context['to_date'] = to_date
            context['company'] = company

        context['search_form'] = form

        return context


import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from helpers.mixins import PermissionMixin


class BIRTDemoReportView(LoginRequiredMixin, PermissionMixin, TemplateView):
    template_name = 'reporting/birt_demo.html'
    permission_required = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['report_url'] = os.environ['REPORT_URL']
        return context

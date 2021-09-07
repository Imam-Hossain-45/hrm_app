from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView

from helpers.mixins import PermissionMixin
from user_management.workflow import Approval
from dashboard.views import map_for_approval


class ApprovalListView(LoginRequiredMixin, PermissionMixin, TemplateView):
    template_name = 'user_management/approvals/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        approvals = Approval(self.request).get()
        approvals = list(map(map_for_approval, approvals))

        context['permissions'] = self.get_current_user_permission_list()
        context['approvals_pending'] = list(
            filter(lambda approval: approval['status'] == 'pending', approvals)
        )
        context['approvals_approved'] = list(
            filter(lambda approval: approval['status'] == 'approved', approvals)
        )
        context['approvals_declined'] = list(
            filter(lambda approval: approval['status'] == 'declined', approvals)
        )

        return context

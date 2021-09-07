from django.contrib.contenttypes.models import ContentType

from user_management.models import Workflow, Approval as ApprovalModel, ApprovalNotification


class Approval:
    _request = None
    _workflow = None
    _content_type = None
    _model = None
    _type = None

    def __init__(self, request, model=None, item_type='leave'):
        """
        Approval class to handle whole approval system all over the project.

        :param request
        :param model
        :param item_type: leave/early-out/late-entry
        """
        print(model)

        permissions = list(
            permission.group for permission in request.user.usergroup_set.all())
        self._request = request
        self._model = model
        self._type = item_type

        try:
            self._content_type = ContentType.objects.get(
                model=model.__class__.__name__)
        except:
            pass

        self._workflow = Workflow.objects.filter(
            content_type=self._content_type,
            workflowvariation__workflowvariationinitiator__initiator__in=permissions
        )

    def set(self) -> None:
        """
        Save an application which needs approval.

        :return: None
        """
        for w in self._workflow:
            for v in w.workflowvariation_set.all():
                for l in v.workflowvariationlevel_set.all():
                    for a in l.workflowapproval_set.all():
                        for u in a.approved_by.user_set.all():
                            approval = ApprovalModel(
                                content_type=self._content_type,
                                item=self._model.id,
                                item_type=self._type,
                                reporting=u.employee,
                                operator=a.next_approval_operator,
                                level=l.level
                            )

                            approval.save()

    def get(self, status_filtering=None) -> ApprovalModel:
        """
        Get a list of approvals.

        :param status_filtering: Filter by status: pending/approved/declined
        :return: <QuerySet: Approval>
        """
        if status_filtering is not None:
            return ApprovalModel.objects.filter(reporting=self._request.user.employee_id, status=status_filtering)

        return ApprovalModel.objects.filter(reporting=self._request.user.employee_id)

    def set_notifications(self, notification_for, content) -> None:
        """
        Set notifications after an approval is approved or declined.

        :param notification_for: Primary key of Leave/Early out/Late entry model
        :param content: Notification content that has been sent
        :return: None
        """

        approval = ApprovalModel.objects.filter(item=notification_for).last()
        workflows = Workflow.objects.filter(content_type=approval.content_type)

        for w in workflows:
            for v in w.workflowvariation_set.all():
                for l in v.workflowvariationlevel_set.all():
                    for n in l.workflownotificationrecipient_set.all():
                        for r in n.notification_recipient.all():
                            for u in r.user_set.all():
                                ApprovalNotification(
                                    to=u.employee, content=content).save()

    def get_notifications(self) -> ApprovalNotification:
        """
        Get notifications of actions of approvals.

        :return: <QuerySet: ApprovalNotification>
        """

        return ApprovalNotification.objects.filter(to=self._request.user.employee)

    def approve_or_decline(self, approve_or_decline, approval_type, item_id) -> None:
        """
        Approve or decline the specified approval.

        :param approve_or_decline: approved/declined
        :param approval_type: leave/early-out/late-entry
        :param item_id: Primary key of Leave/Early out/Late entry model
        :return: None
        """

        if self._request.user.is_superuser:
            ApprovalModel.objects.filter(
                item=item_id,
                item_type=approval_type
            ).update(status=approve_or_decline)
        else:
            my_approval = ApprovalModel.objects.filter(
                item=item_id,
                item_type=approval_type,
                reporting=self._request.user.employee
            )
            my_approval.update(status=approve_or_decline)

            i = my_approval.last().level

            if i > 1:
                for j in range(1, i):
                    ApprovalModel.objects.filter(
                        item=item_id,
                        item_type=approval_type,
                        level=j
                    ).update(status=approve_or_decline)

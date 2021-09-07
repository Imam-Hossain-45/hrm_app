from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from helpers.mixins import PermissionMixin
from user_management.forms import WorkflowVariationInitiatorForm, levelFormset, UpdateLevelFormset
from user_management.models import (
    Workflow, WorkflowVariation, WorkflowVariationInitiator, WorkflowVariationLevel,
    WorkflowApproval, WorkflowNotificationRecipient
)
from helpers.functions import get_organizational_structure
from django.contrib import messages


def workflow_form_data(self=None, instance=None):
    formset = self.formset(self.request.POST)
    data = {'workflowvariationlevel_set-TOTAL_FORMS': self.request.POST['workflowvariationlevel_set-TOTAL_FORMS']}
    data.update({
        'workflowvariationlevel_set-INITIAL_FORMS': self.request.POST['workflowvariationlevel_set-INITIAL_FORMS'],
        'workflowvariationlevel_set-MIN_NUM_FORMS': self.request.POST['workflowvariationlevel_set-MIN_NUM_FORMS'],
    })

    for i, level_form in enumerate(formset):
        data['workflowvariationlevel_set-'+str(i)+'-level'] = self.request.POST['workflowvariationlevel_set-'+str(i)+'-level']
        data['workflowvariationlevel_set-'+str(i)+'-id'] = self.request.POST['workflowvariationlevel_set-'+str(i)+'-id']
        if self.request.POST.get('workflowvariationlevel_set-' + str(i) + '-DELETE'):
            data['workflowvariationlevel_set-' + str(i) + '-DELETE'] = \
                self.request.POST['workflowvariationlevel_set-' + str(i) + '-DELETE']
        else:
            data['workflowvariationlevel_set-' + str(i) + '-DELETE'] = ''

        data.update({
            'workflow-approval-workflowvariationlevel_set-' + str(i) + '-workflowapproval_set-TOTAL_FORMS':
                self.request.POST['workflow-approval-workflowvariationlevel_set-' + str(i)
                                  + '-workflowapproval_set-TOTAL_FORMS'],
            'workflow-approval-workflowvariationlevel_set-' + str(i) + '-workflowapproval_set-INITIAL_FORMS':
                self.request.POST['workflow-approval-workflowvariationlevel_set-' + str(i)
                                  + '-workflowapproval_set-INITIAL_FORMS'],
            'workflow-approval-workflowvariationlevel_set-' + str(i) + '-workflowapproval_set-MIN_NUM_FORMS':
                self.request.POST['workflow-approval-workflowvariationlevel_set-' + str(i)
                                  + '-workflowapproval_set-MIN_NUM_FORMS'],
            'workflow-recipient-workflowvariationlevel_set-' + str(i) +
            '-workflownotificationrecipient_set-TOTAL_FORMS':
                self.request.POST['workflow-recipient-workflowvariationlevel_set-' + str(i) +
                                  '-workflownotificationrecipient_set-TOTAL_FORMS'],
            'workflow-recipient-workflowvariationlevel_set-' + str(i) +
            '-workflownotificationrecipient_set-INITIAL_FORMS':
                self.request.POST['workflow-recipient-workflowvariationlevel_set-' + str(i) +
                                  '-workflownotificationrecipient_set-INITIAL_FORMS'],
            'workflow-recipient-workflowvariationlevel_set-' + str(i) +
            '-workflownotificationrecipient_set-MAX_NUM_FORMS':
                self.request.POST['workflow-recipient-workflowvariationlevel_set-' + str(i) +
                                  '-workflownotificationrecipient_set-MAX_NUM_FORMS'],
            'workflow-recipient-workflowvariationlevel_set-' + str(i) +
            '-workflownotificationrecipient_set-MIN_NUM_FORMS':
                self.request.POST['workflow-recipient-workflowvariationlevel_set-' + str(i) +
                                  '-workflownotificationrecipient_set-MIN_NUM_FORMS']
        })
        approved_formset = self.request.POST[
            'workflow-approval-workflowvariationlevel_set-' + str(i) + '-workflowapproval_set-TOTAL_FORMS'
        ]

        for j in range(int(approved_formset)):
            approved_by = 'workflow-approval-workflowvariationlevel_set-' + str(i) +\
                          '-workflowapproval_set-' + str(j) + '-approved_by'
            operand_my = 'workflow-approval-workflowvariationlevel_set-' + str(i) +\
                         '-workflowapproval_set-' + str(j) + '-next_approval_operator'

            data[approved_by] = \
                int(self.request.POST[approved_by]) if self.request.POST[approved_by] not in ['', None] else None
            data[operand_my] = self.request.POST[operand_my]
            data['workflow-approval-workflowvariationlevel_set-'+str(i)+'-workflowapproval_set-'+str(j)+'-id'] = \
                self.request.POST['workflow-approval-workflowvariationlevel_set-'
                                  + str(i)+'-workflowapproval_set-'+str(j)+'-id']
            approval_delete = 'workflow-approval-workflowvariationlevel_set-'+str(i) + \
                              '-workflowapproval_set-'+str(j)+'-DELETE'
            if self.request.POST.get(approval_delete):
                data[approval_delete] = self.request.POST[approval_delete]
            else:
                data[approval_delete] = ''

        recipients_formset = self.request.POST["workflow-recipient-workflowvariationlevel_set-" + str(
                i) + "-workflownotificationrecipient_set-TOTAL_FORMS"]

        for k in range(int(recipients_formset)):
            data["workflow-recipient-workflowvariationlevel_set-" + str(
                    i) + "-workflownotificationrecipient_set-" + str(k) + "-notification_recipient"] = \
                [int(value) for value in self.request.POST.getlist(
                    "workflow-recipient-workflowvariationlevel_set-" + str(i) +
                    "-workflownotificationrecipient_set-" + str(k) + "-notification_recipient")]

    if instance:
        return self.formset(data, instance)
    return self.formset(data)


def workflow_formset_validator(self, formset):
    for i, level_form in enumerate(formset):
        try:
            deleted = self.request.POST['workflowvariationlevel_set-' + str(i) + '-DELETE']
        except:
            deleted = None

        if deleted:
            continue

        approved_formset = self.request.POST[
            "workflow-approval-workflowvariationlevel_set-" + str(i) + "-workflowapproval_set-TOTAL_FORMS"
        ]

        approved_by_list = []

        for j in range(int(approved_formset)):
            approved_by = self.request.POST[
                "workflow-approval-workflowvariationlevel_set-" + str(i) +
                "-workflowapproval_set-" + str(j) + "-approved_by"
            ]
            next_approval_operator = self.request.POST[
                "workflow-approval-workflowvariationlevel_set-" + str(i) +
                "-workflowapproval_set-" + str(j) + "-next_approval_operator"
            ]
            if approved_by in ['', None]:
                message = "Error at level " + str(i+1) + ": Approved by field cannot be blank. Field: " + str(j+1)
                return False, message
            if approved_by in approved_by_list:
                message = "Error at level " + str(i+1) + \
                          ": Cannot select on approval authority more than once in a level. Field: " + str(j+1)
                return False, message

            if j == int(approved_formset) - 1:
                if next_approval_operator not in ['', None]:
                    message = "Error at level " + str(i+1) + \
                              ": No approved by to add with " + next_approval_operator + " operator. Field: " + str(j+1)
                    return False, message
            else:
                message = "Error at level " + str(i+1) + \
                          ": Could not add to approval authority, as no operator was given in field: " + str(j+1)
                if next_approval_operator in ['', None]:
                    return False, message
            approved_by_list.append(approved_by)

    return True, "Valid form"


class WorkflowListView(ListView, PermissionMixin, LoginRequiredMixin):
    """List of role hierarchies."""

    template_name = 'user_management/workflow/list.html'
    model = ContentType
    context_object_name = 'content_types'
    permission_required = ['add_workflow', 'change_workflow', 'delete_workflow', 'view_workflow']

    def get_queryset(self):
        content_types = ContentType.objects.all()
        queryset = []

        for x in content_types:
            try:
                model = x.model_class()._meta.verbose_name.capitalize()
                queryset.append({
                    'model': model,
                    'id': x.id
                })
            except:
                pass

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['defined_contents'] = [content.content_type.id for content in Workflow.objects.filter(status='defined')]

        return context


class WorkflowCreateView(LoginRequiredMixin, PermissionMixin, FormView):
    """Show the form to create a mew workflow variation."""

    template_name = 'user_management/workflow/create.html'
    form_class = WorkflowVariationInitiatorForm
    formset = levelFormset
    success_url = reverse_lazy('user_management:workflows_list')
    permission_required = 'add_workflow'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['org_items_list'] = get_organizational_structure()
        context['permissions'] = self.get_current_user_permission_list()
        context['formset'] = self.formset
        try:
            context['workflow'] = Workflow.objects.get(content_type_id=self.kwargs['id'])
        except:
            pass
        context['workflow_cu_type'] = 'create'

        return context

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['selected_initials'] = [int(initiator_id) for initiator_id in self.request.POST.getlist('initiator')]

        form = self.form_class(request.POST or None)
        context['form'] = form

        level_formset = workflow_form_data(self=self)
        context['formset'] = level_formset
        try:
            context['workflow'] = Workflow.objects.get(content_type_id=self.kwargs['id'])
        except:
            pass
        context['workflow_cu_type'] = 'create'

        if not form.is_valid() or not level_formset.is_valid():
            return render(request, self.template_name, context)

        valid, message = workflow_formset_validator(self=self, formset=level_formset)
        if valid is False:
            messages.error(request, message)
            return render(request, self.template_name, context)

        workflow_obj, created = Workflow.objects.update_or_create(content_type_id=self.kwargs['id'],
                                                                  defaults={
                                                                      'status': 'defined'
                                                                  })
        workflow_variation_obj = WorkflowVariation.objects.create(workflow=workflow_obj)

        initiators = self.request.POST.getlist('initiator')
        if self.request.POST.getlist('initiator') not in ['', None]:
            for initiator in initiators:
                WorkflowVariationInitiator.objects.create(workflow_variation=workflow_variation_obj,
                                                          initiator_id=initiator)

        for i, level_form in enumerate(level_formset):
            level_obj = WorkflowVariationLevel.objects.create(workflow_variation=workflow_variation_obj,
                                                              level=i + 1)

            recipients_formset = self.request.POST["workflow-recipient-workflowvariationlevel_set-" + str(
                i) + "-workflownotificationrecipient_set-TOTAL_FORMS"]

            for k in range(int(recipients_formset)):
                recipients = self.request.POST.getlist(
                    "workflow-recipient-workflowvariationlevel_set-" + str(
                        i) + "-workflownotificationrecipient_set-" + str(k) + "-notification_recipient")
                if recipients:
                    workflow_notification_obj = WorkflowNotificationRecipient.objects.create(
                        workflow_variation_level=level_obj
                    )
                    workflow_notification_obj.notification_recipient.set(recipients)

            approved_formset = self.request.POST[
                "workflow-approval-workflowvariationlevel_set-" + str(i) + "-workflowapproval_set-TOTAL_FORMS"]

            for j in range(int(approved_formset)):
                approved_by = self.request.POST[
                    "workflow-approval-workflowvariationlevel_set-" +
                    str(i) + "-workflowapproval_set-" + str(j) + "-approved_by"]
                next_approval_operator = self.request.POST[
                    "workflow-approval-workflowvariationlevel_set-" +
                    str(i) + "-workflowapproval_set-" + str(j) + "-next_approval_operator"]
                WorkflowApproval.objects.create(workflow_variation_level=level_obj, approved_by_id=approved_by,
                                                next_approval_operator=next_approval_operator)

        return redirect(self.success_url)


class WorkflowUpdateView(LoginRequiredMixin, PermissionMixin, UpdateView):
    """Show the form to update the specified hierarchy."""

    template_name = 'user_management/workflow/update.html'
    form_class = WorkflowVariationInitiatorForm
    model = WorkflowVariation
    formset = UpdateLevelFormset
    permission_required = 'add_workflow'

    def get_workflow_variation(self, pk):
        return WorkflowVariation.objects.get(id=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['org_items_list'] = get_organizational_structure()
        context['permissions'] = self.get_current_user_permission_list()
        context['selected_initials'] = \
            [initiator.initiator_id for initiator in
             WorkflowVariationInitiator.objects.filter(workflow_variation_id=self.kwargs['pk'])]
        context['formset'] = self.formset(instance=self.get_workflow_variation(self.kwargs['pk']))
        try:
            context['workflow'] = Workflow.objects.get(content_type_id=self.kwargs['content_id'])
        except:
            pass

        context['create_url_id'] = self.kwargs['content_id']
        context['workflow_cu_type'] = 'update'

        return context

    def post(self, request, *args, **kwargs):
        context = {'permissions': self.get_current_user_permission_list()}
        context['org_items_list'] = get_organizational_structure()
        context['create_url_id'] = self.kwargs['content_id']
        context['selected_initials'] = [int(initiator_id) for initiator_id in self.request.POST.getlist('initiator')]
        form = self.form_class(request.POST or None)
        context['form'] = form

        update_level_formset = workflow_form_data(self=self, instance=self.get_workflow_variation(self.kwargs['pk']))
        context['formset'] = update_level_formset
        try:
            context['workflow'] = Workflow.objects.get(content_type_id=self.kwargs['id'])
        except:
            pass
        context['workflow_cu_type'] = 'update'
        print(update_level_formset.is_valid())
        print(update_level_formset.errors)
        if not form.is_valid() or not update_level_formset.is_valid():
            return render(request, self.template_name, context)

        try:
            workflow_variation_obj = WorkflowVariation.objects.get(id=self.kwargs['pk'])
        except:
            return render(request, self.template_name, context)

        valid, message = workflow_formset_validator(self=self, formset=update_level_formset)
        if valid is False:
            messages.error(request, message)
            return render(request, self.template_name, context)

        initiators = self.request.POST.getlist('initiator')
        workflow_variation_init_qs = WorkflowVariationInitiator.objects.filter(
            workflow_variation=workflow_variation_obj
        )
        if workflow_variation_init_qs.exists():
            for wfi in workflow_variation_init_qs:
                if str(wfi.initiator.id) not in initiators:
                    wfi.delete()

        if self.request.POST.getlist('initiator') not in ['', None]:
            for initiator in initiators:
                WorkflowVariationInitiator.objects.update_or_create(workflow_variation=workflow_variation_obj,
                                                                    initiator_id=initiator)
        level = 1
        for i, level_form in enumerate(update_level_formset):
            try:
                deleted = self.request.POST['workflowvariationlevel_set-' + str(i) + '-DELETE']
            except:
                deleted = None

            obj_id = self.request.POST['workflowvariationlevel_set-' + str(i) + '-id']

            if deleted:
                try:
                    WorkflowVariationLevel.objects.get(id=obj_id).delete()
                except:
                    pass
                continue

            level_obj, created = WorkflowVariationLevel.objects.update_or_create(
                id=obj_id, workflow_variation=workflow_variation_obj, defaults={'level': level}
            )
            recipients_formset = self.request.POST["workflow-recipient-workflowvariationlevel_set-" + str(
                i) + "-workflownotificationrecipient_set-TOTAL_FORMS"]

            for k in range(int(recipients_formset)):
                recipients = self.request.POST.getlist(
                    "workflow-recipient-workflowvariationlevel_set-" + str(
                        i) + "-workflownotificationrecipient_set-" + str(k) + "-notification_recipient")
                if not recipients:
                    try:
                        WorkflowNotificationRecipient.objects.get(workflow_variation_level=level_obj).delete()
                    except:
                        pass
                else:
                    try:
                        workflow_notification_obj, created = WorkflowNotificationRecipient.objects.get_or_create(
                            workflow_variation_level=level_obj
                        )
                        workflow_notification_obj.notification_recipient.set(recipients)
                    except:
                        messages.error(request, 'Error in Workflow Notification Recipient saving')
                        return render(request, self.template_name, context)

            approved_formset = self.request.POST[
                "workflow-approval-workflowvariationlevel_set-" + str(i) + "-workflowapproval_set-TOTAL_FORMS"]

            for j in range(int(approved_formset)):
                try:
                    deleted = self.request.POST['workflow-approval-workflowvariationlevel_set-' + str(i) +
                                                '-workflowapproval_set-' + str(j) + '-DELETE']
                except:
                    deleted = None

                obj_id = self.request.POST['workflow-approval-workflowvariationlevel_set-' + str(i) +
                                           '-workflowapproval_set-' + str(j) + '-id']

                if deleted:
                    try:
                        WorkflowApproval.objects.get(id=obj_id).delete()
                        approved_by = self.request.POST[
                            "workflow-approval-workflowvariationlevel_set-" +
                            str(i) + "-workflowapproval_set-" + str(j-1) + "-approved_by"]
                        if j == int(approved_formset) - 1:
                            WorkflowApproval.objects.update_or_create(workflow_variation_level=level_obj,
                                                                      approved_by_id=approved_by,
                                                                      defaults={
                                                                          'next_approval_operator': ''
                                                                      })
                    except:
                        pass
                    continue

                approved_by = self.request.POST[
                    "workflow-approval-workflowvariationlevel_set-" +
                    str(i) + "-workflowapproval_set-" + str(j) + "-approved_by"]
                next_approval_operator = self.request.POST[
                    "workflow-approval-workflowvariationlevel_set-" +
                    str(i) + "-workflowapproval_set-" + str(j) + "-next_approval_operator"]
                try:
                    WorkflowApproval.objects.update_or_create(workflow_variation_level=level_obj,
                                                              approved_by_id=approved_by,
                                                              defaults={
                                                                  'next_approval_operator': next_approval_operator
                                                              })
                except Exception as e:
                    print(e)
                    messages.error(request,
                                   'Error in Workflow Approval saving for: level ' + str(i+1) + ': line:' + str(j+1))
                    return render(request, self.template_name, context)
            level += 1
        return redirect(reverse_lazy('user_management:workflows_create', kwargs={'id': self.kwargs['content_id']}))


class WorkflowDeleteView(LoginRequiredMixin, PermissionMixin, DeleteView):
    """Delete the specified role."""

    model = Workflow
    permission_required = 'delete_workflow'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def post(self, request, *args, **kwargs):
        try:
            WorkflowVariation.objects.get(id=self.kwargs['pk']).delete()
            if not WorkflowVariation.objects.filter(workflow__content_type_id=self.kwargs['content_id']).exists():
                workflow_obj = Workflow.objects.get(content_type_id=self.kwargs['content_id'])
                workflow_obj.status = 'undefined'
                workflow_obj.save()
        except:
            pass
        return redirect(reverse_lazy('user_management:workflows_create', kwargs={'id': self.kwargs['content_id']}))

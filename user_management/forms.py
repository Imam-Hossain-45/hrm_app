import os
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, SetPasswordForm
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from setting.models import Company
from user_management.models import (User, WorkflowVariationInitiator, WorkflowApproval,
                                    WorkflowNotificationRecipient, WorkflowVariationLevel, WorkflowVariation)


class UserCreationCreateForm(forms.ModelForm):
    """Form to create a user."""

    send_credential = forms.BooleanField(required=False, label='Send credential to email')

    def send_email(self, model):
        message = render_to_string('user_management/user_creation/mail_account_created.html', {
            'name': model,
            'email': model.email,
            'password': model.password,
            'login_url': os.environ['APP_URL'] + str(reverse_lazy('accounts:login'))
        })

        send_mail(
            subject='Your account has been created',
            from_email=os.environ['EMAIL_FROM_EMAIL'],
            recipient_list=[model.email],
            html_message=message,
            message=message
        )

    class Meta:
        model = User
        fields = '__all__'
        labels = {
            'employee': 'Select Employee'
        }


class UserCreationUpdateForm(forms.ModelForm):
    """Form to update a user."""

    password = ReadOnlyPasswordHashField()
    send_credential = forms.BooleanField(required=False, label='Send credential to email')
    companies = forms.ModelMultipleChoiceField(
        queryset=Company.objects,
        required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        company_choices = []

        super().__init__(*args, **kwargs)

        for company in self.fields['companies'].choices:
            self.fields['role_for_company_' + str(company[0] - 1)] = forms.ModelMultipleChoiceField(
                queryset=Group.objects,
                required=False
            )

        if user.usergroup_set.count() > 0:
            for company in self.fields['companies'].choices:
                for group in user.usergroup_set.all():
                    if company[0] == group.company_id:
                        role_choices = []
                        company += (True,)

                        for role in self.fields['role_for_company_' + str(company[0] - 1)].choices:
                            if role[0] == group.group_id:
                                role += (True,)

                            role_choices.append(role)

                        self.fields['role_for_company_' + str(company[0] - 1)].choices = role_choices

                company_choices.append(company)

            self.fields['companies'].choices = company_choices

    def role_fields(self):
        for name in self.fields:
            if name.startswith('role_for_company_'):
                yield (self[name])

    class Meta:
        model = User
        fields = (
            'name',
            'date_of_birth',
            'phone',
            'email',
            'user_type',
            'employee',
            'management',
            'is_staff',
            'status',
            'dashboard',
            'self_panel'
        )
        labels = {
            'employee': 'Select Employee'
        }


class UserCreationPasswordChangeForm(SetPasswordForm):
    send_to_email = forms.BooleanField(required=False, label='Send password to email')

    def send_email(self, user):
        message = render_to_string('user_management/user_creation/mail_password_changed.html', {
            'name': user,
            'password': self.cleaned_data["new_password1"]
        })

        send_mail(
            subject='Your password has been changed by an admin',
            from_email=os.environ['EMAIL_FROM_EMAIL'],
            recipient_list=[user.email],
            html_message=message,
            message=message
        )


class WorkflowVariationInitiatorForm(forms.ModelForm):
    class Meta:
        model = WorkflowVariationInitiator
        fields = ('initiator',)


class BaseChildrenFormset(BaseInlineFormSet):
    def add_fields(self, form, index):
        super(BaseChildrenFormset, self).add_fields(form, index)
        # save the formset in the 'nested' property
        form.recipient = RecipientFormset(
            instance=form.instance or None,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix='workflow-recipient-%s-%s' % (
                form.prefix,
                RecipientFormset.get_default_prefix()),
        )
        if form.instance.pk is None:
            ApprovalFormset = ApprovalFunction(value=1)
        else:
            ApprovalFormset = ApprovalFunction(value=0)

        form.nested = ApprovalFormset(
            instance=form.instance or None,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix='workflow-approval-%s-%s' % (
                form.prefix,
                ApprovalFormset.get_default_prefix()),
        )


levelFormset = inlineformset_factory(WorkflowVariation, WorkflowVariationLevel, fields='__all__',
                                     formset=BaseChildrenFormset, extra=1)

UpdateLevelFormset = inlineformset_factory(WorkflowVariation, WorkflowVariationLevel, fields='__all__',
                                           formset=BaseChildrenFormset, extra=0)

RecipientFormset = inlineformset_factory(WorkflowVariationLevel, WorkflowNotificationRecipient,
                                         fields='__all__', max_num=1)


def ApprovalFunction(value):
    return inlineformset_factory(WorkflowVariationLevel, WorkflowApproval, fields='__all__', extra=value)

from django import forms
from leave.models import *
from setting.models import *
from attendance.models import ScheduleMaster
from django.core.validators import EMPTY_VALUES


class LeaveEntryForm(forms.ModelForm):
    leave_type = forms.ChoiceField()

    class Meta:
        model = LeaveEntry
        fields = ('start_date', 'end_date', 'start_time', 'end_time', 'reason_of_leave', 'attachment')

    def __init__(self, choices, *args, **kwargs):
        self.leave_type = choices
        super(LeaveEntryForm, self).__init__(*args, **kwargs)
        self.fields['leave_type'].choices = self.leave_type

    def clean(self):
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        if start_date not in EMPTY_VALUES and end_date not in EMPTY_VALUES:
            if start_date > end_date:
                self._errors['end_date'] = self.error_class(['End date should be greater than start date.'])


class LeaveApprovalForm(forms.ModelForm):
    class Meta:
        model = LeaveApprovalComment
        fields = ('comment',)


class SearchForm(forms.Form):
    employee = forms.CharField(required=False)
    from_date = forms.DateField(required=False, label='Select Date')
    to_date = forms.DateField(required=False)
    company = forms.ModelChoiceField(required=False, queryset=Company.objects.filter(status='active'), label='Select Company')
    division = forms.ModelChoiceField(required=False, queryset=Division.objects.filter(status='active'), label='Select Division')
    department = forms.ModelChoiceField(required=False, queryset=Department.objects.filter(status='active'), label='Select Department')
    business_unit = forms.ModelChoiceField(required=False, queryset=BusinessUnit.objects.filter(status='active'), label='Select Business Unit')
    branch = forms.ModelChoiceField(required=False, queryset=Branch.objects.filter(status='active'), label='Select Branch')
    schedule = forms.ModelChoiceField(required=False, queryset=ScheduleMaster.objects.filter(status=True), label='Select Schedule Type')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].empty_label = 'All'
        self.fields['division'].empty_label = 'All'
        self.fields['department'].empty_label = 'All'
        self.fields['business_unit'].empty_label = 'All'
        self.fields['branch'].empty_label = 'All'
        self.fields['schedule'].empty_label = 'All'

    def clean(self):
        from_date = self.cleaned_data.get('from_date')
        to_date = self.cleaned_data.get('to_date')
        if from_date not in EMPTY_VALUES and to_date not in EMPTY_VALUES:
            if from_date > to_date:
                self._errors['to_date'] = self.error_class(['To date should be greater than from date.'])

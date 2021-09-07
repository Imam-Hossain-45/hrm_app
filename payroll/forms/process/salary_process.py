from django import forms
from setting.models import Company, Division, Department, BusinessUnit, Branch
from attendance.models import ScheduleMaster


class SearchForm(forms.Form):
    employee = forms.CharField(required=False)
    start_date = forms.DateField()
    end_date = forms.DateField()
    company = forms.ModelChoiceField(queryset=Company.objects.all(), label='Select Company', required=False)
    division = forms.ModelChoiceField(queryset=Division.objects.all(), label='Select Division', required=False)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), label='Select Department', required=False)
    business_unit = forms.ModelChoiceField(queryset=BusinessUnit.objects.all(), label='Select Business Unit',
                                           required=False)
    branch = forms.ModelChoiceField(queryset=Branch.objects.all(), label='Select Branch', required=False)
    schedule = forms.ModelChoiceField(queryset=ScheduleMaster.objects.all(), label='Select Schedule Type',
                                      required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].empty_label = 'All'
        self.fields['division'].empty_label = 'All'
        self.fields['department'].empty_label = 'All'
        self.fields['business_unit'].empty_label = 'All'
        self.fields['branch'].empty_label = 'All'
        self.fields['schedule'].empty_label = 'All'

    def my_is_valid(self):
        self.full_clean()
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')

        if end_date < start_date:
            return False
        return True


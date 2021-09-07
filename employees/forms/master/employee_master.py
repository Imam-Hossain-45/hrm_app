from django import forms
from employees import models as emp_models
from django.core.validators import EMPTY_VALUES


class EmployeeIdentificationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=20, error_messages={'required': "The field is required."},
                                 widget=forms.TextInput(attrs={'placeholder': 'First Name'}), label='Name')
    middle_name = forms.CharField(max_length=20, required=False,
                                  widget=forms.TextInput(attrs={'placeholder': 'Middle Name'}))
    last_name = forms.CharField(max_length=20, required=False,
                                widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))

    class Meta:
        model = emp_models.EmployeeIdentification
        fields = ('first_name', 'middle_name', 'last_name', 'employee_code',
                  'title', 'display_name', 'employee_id', 'gender', 'profile_picture')


class EmployeeJobForm(forms.ModelForm):
    class Meta:
        model = emp_models.JobInformation
        fields = ('company', 'business_unit', 'division', 'department', 'project', 'designation', 'report_to',
                  'additional_report_to', 'pay_group', 'pay_scale', 'pay_grade', 'job_status', 'employment_type',
                  'date_of_offer', 'date_of_joining')


class EmploymentForm(forms.ModelForm):
    class Meta:
        model = emp_models.Employment
        fields = ('confirmation_after', 'confirmation_after_unit', 'confirmation_date', 'date_of_actual_confirmation')

    def clean(self):
        if self.cleaned_data.get('confirmation_date') not in EMPTY_VALUES and\
                self.cleaned_data.get('date_of_actual_confirmation') in EMPTY_VALUES:
            self.cleaned_data['date_of_actual_confirmation'] = self.cleaned_data['confirmation_date']

        return self.cleaned_data


class EmploymentContractForm(forms.ModelForm):
    class Meta:
        model = emp_models.EndOfContract
        fields = ('due_on', 'date_of_settlement', 'effective_date')


class EmploymentSeparationForm(forms.ModelForm):
    date_of_sack = forms.DateField(required=False)
    date_of_resign = forms.DateField(required=False)
    date_of_settlement = forms.DateField(required=False)
    effective_date = forms.DateField(required=False)

    class Meta:
        model = emp_models.Separation
        fields = ('type_of_resign', 'date_of_sack', 'date_of_resign', 'date_of_settlement', 'effective_date')
        widgets = {
            'type_of_resign': forms.RadioSelect()
        }

    def clean(self):
        type_of_resign = self.cleaned_data.get('type_of_resign')
        if type_of_resign == 'sack':
            date_of_sack = self.cleaned_data.get('date_of_sack')
            date_of_settlement = self.cleaned_data.get('date_of_settlement')
            effective_date = self.cleaned_data.get('effective_date')
            self.fields['date_of_resign'].empty_label = None
            if date_of_sack in EMPTY_VALUES:
                self._errors['date_of_sack'] = self.error_class(['This field is required'])
            if date_of_settlement in EMPTY_VALUES:
                self._errors['date_of_settlement'] = self.error_class(['This field is required'])
            if effective_date in EMPTY_VALUES:
                self._errors['effective_date'] = self.error_class(['This field is required'])

        if type_of_resign == 'resign':
            date_of_resign = self.cleaned_data.get('date_of_resign')
            date_of_settlement = self.cleaned_data.get('date_of_settlement')
            effective_date = self.cleaned_data.get('effective_date')
            if date_of_resign in EMPTY_VALUES:
                self._errors['date_of_resign'] = self.error_class(['This field is required'])
            if date_of_settlement in EMPTY_VALUES:
                self._errors['date_of_settlement'] = self.error_class(['This field is required'])
            if effective_date in EMPTY_VALUES:
                self._errors['effective_date'] = self.error_class(['This field is required'])

        if type_of_resign == 'accidental_separation':
            date_of_settlement = self.cleaned_data.get('date_of_settlement')
            effective_date = self.cleaned_data.get('effective_date')
            if date_of_settlement in EMPTY_VALUES:
                self._errors['date_of_settlement'] = self.error_class(['This field is required'])
            if effective_date in EMPTY_VALUES:
                self._errors['effective_date'] = self.error_class(['This field is required'])

        return self.cleaned_data


class EmploymentRetirementForm(forms.ModelForm):
    class Meta:
        model = emp_models.Retirement
        fields = ('due_on', 'date_of_settlement', 'effective_date')

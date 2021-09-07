from django import forms
from employees import models as emp_models
from django.core.validators import EMPTY_VALUES


class EmploymentHistoryForm(forms.ModelForm):
    class Meta:
        model = emp_models.EmploymentHistory
        fields = (
            'organization', 'designation', 'department', 'start_from', 'to', 'salary')

    def clean(self):
        start_from = self.cleaned_data.get('start_from')
        to = self.cleaned_data.get('to')
        if start_from not in EMPTY_VALUES and to not in EMPTY_VALUES:
            if start_from > to:
                self._errors['to'] = self.error_class(['To date should be greater than from date.'])

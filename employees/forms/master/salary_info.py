from django import forms
from employees import models as emp_models
from django.core.validators import EMPTY_VALUES


class PaymentForm(forms.ModelForm):
    class Meta:
        model = emp_models.Payment
        fields = (
            'payment_mode', 'pay_schedule', 'employee_bank_name', 'employee_bank_AC_name', 'bank_branch_code', 'bank_AC_no',
            'routing_number')


class SalaryStructureForm(forms.ModelForm):
    class Meta:
        model = emp_models.SalaryStructure
        fields = (
            'salary_group', 'from_date', 'to_date', 'bonus_group', 'reason_of_salary_modification')

    def clean(self):
        from_date = self.cleaned_data.get('from_date')
        to_date = self.cleaned_data.get('to_date')
        if from_date not in EMPTY_VALUES and to_date not in EMPTY_VALUES:
            if from_date > to_date:
                self._errors['to_date'] = self.error_class(['To date should be greater than from date.'])


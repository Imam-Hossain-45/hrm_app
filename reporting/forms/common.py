from django import forms

from attendance.models import ScheduleMaster
from employees.models import EmployeeIdentification
from setting.models import Branch, BusinessUnit, Company, Department, Division
from .fields import MultipleObjectCSVField


class EmployeeFilterForm(forms.Form):
    """Form to filter through the report's target employees."""
    from_date = forms.DateField()
    to_date = forms.DateField()

    employees = MultipleObjectCSVField(
        queryset=EmployeeIdentification.objects.all(),
        to_field_name='employee_id',
        required=False,
    )

    company = forms.ModelChoiceField(
        queryset=Company.objects.filter(status='active'),
        required=False,
    )
    division = forms.ModelChoiceField(
        queryset=Division.objects.filter(status='active'),
        required=False,
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(status='active'),
        required=False,
    )
    business_unit = forms.ModelChoiceField(
        queryset=BusinessUnit.objects.filter(status='active'),
        required=False,
    )
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.filter(status='active'),
        required=False,
    )
    # The ScheduleMaster.status has changed.
    # schedule = forms.ModelChoiceField(
    #     queryset=ScheduleMaster.objects.filter(status=True),
    #     required=False,
    # )

    def clean(self):
        """Validate that at least one of the non-required fields is bound."""
        cleaned_data = super().clean()
        employees = cleaned_data.get('employees')
        company = cleaned_data.get('company')
        division = cleaned_data.get('division')
        department = cleaned_data.get('department')
        business_unit = cleaned_data.get('business_unit')
        branch = cleaned_data.get('branch')
        schedule = cleaned_data.get('schedule')

        at_least_1 = (
                employees or company or division or department
                or business_unit or branch or schedule
        )

        if not at_least_1:
            raise forms.ValidationError(
                'None of the employee-filtering options have been activated'
            )

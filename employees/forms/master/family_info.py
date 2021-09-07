from django import forms
from employees import models as emp_models


class FamilyForm(forms.ModelForm):
    class Meta:
        model = emp_models.Family
        fields = (
            'name_of_family_member', 'relationship_with_employee', 'DOB', 'age', 'gender', 'employed', 'dependent')

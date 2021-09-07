from django import forms
from employees import models as emp_models
from django.core.validators import EMPTY_VALUES


class AttendanceManageForm(forms.ModelForm):
    class Meta:
        model = emp_models.Attendance
        fields = ('schedule_type', 'punching_id', 'calendar_master')


class LeaveManageForm(forms.ModelForm):
    class Meta:
        model = emp_models.LeaveManage
        fields = ('leave_group', 'overtime', 'overtime_group', 'deduction', 'deduction_group')

    def clean(self):
        # validate the overtime
        overtime = self.cleaned_data.get('overtime')
        if overtime:
            if self.cleaned_data.get('overtime_group') in EMPTY_VALUES:
                self._errors['overtime_group'] = self.error_class(['This field is required'])
        overtime_group = self.cleaned_data.get('overtime_group')
        if overtime_group:
            if overtime is not True:
                self._errors['overtime'] = self.error_class(['This field is required'])

        # validate the deduction
        deduction = self.cleaned_data.get('deduction')
        if deduction:
            if self.cleaned_data.get('deduction_group') in EMPTY_VALUES:
                self._errors['deduction_group'] = self.error_class(['This field is required'])
        deduction_group = self.cleaned_data.get('deduction_group')
        if deduction_group:
            if deduction is not True:
                self._errors['deduction'] = self.error_class(['This field is required'])

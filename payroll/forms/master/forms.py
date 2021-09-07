from django import forms
from payroll.models import (Component, SalaryGroup, SalaryGroupComponent, DeductionComponent, DeductionGroup,
                            BonusComponent, BonusGroup, AbsentSetting, LateSetting, LateSlab, EarlyOutSetting,
                            EarlyOutSlab, UnderWorkSlab)
from user_management.models import User
from setting.models import Department, Division, Branch


class EmployeeSpecifyForm(forms.Form):
    employee = forms.ModelChoiceField(
        User.objects.all(),
        label='Employee',
        required=True,
    )


class EmployeeFilterForm(forms.Form):
    division = forms.ModelChoiceField(
        Division.objects.all(),
        required=False,
    )
    department = forms.ModelChoiceField(
        Department.objects.all(),
        required=False,
    )
    branch = forms.ModelChoiceField(
        Branch.objects.all(),
        required=False,
    )


class SalaryGroupCreateForm(forms.ModelForm):
    component = forms.ModelMultipleChoiceField(
        queryset=Component.objects,
        required=False
    )

    class Meta:
        model = SalaryGroup
        fields = ('name', 'short_code', 'description', 'status')

        error_messages = {
            'title': {'required': 'Title field is required.'}
        }

    def my_is_valid(self):
        self.full_clean()
        name = self.cleaned_data.get('name')
        if not name:
            return False
        return True


class SalaryGroupSettingsUpdateForm(forms.ModelForm):
    class Meta:
        model = SalaryGroupComponent
        fields = ('condition_type', 'mapping_policy')


class DeductionGroupCreateForm(forms.ModelForm):
    absent_component = forms.ModelChoiceField(
        DeductionComponent.objects.filter(deduction_component_type='absent'),
        required=False
    )
    late_component = forms.ModelChoiceField(
        DeductionComponent.objects.filter(deduction_component_type='late'),
        required=False
    )
    early_out_component = forms.ModelChoiceField(
        DeductionComponent.objects.filter(deduction_component_type='early-out'),
        required=False
    )
    under_work_component = forms.ModelChoiceField(
        DeductionComponent.objects.filter(deduction_component_type='under-work'),
        required=False
    )
    other_component = forms.ModelChoiceField(
        DeductionComponent.objects.filter(deduction_component_type='other'),
        required=False
    )

    class Meta:
        model = DeductionGroup
        fields = ('name', 'short_code', 'description', 'status')

        error_messages = {
            'title': {'required': 'Title field is required.'}
        }

    def my_is_valid(self):
        self.full_clean()
        name = self.cleaned_data.get('name')
        if not name:
            return False
        return True


class AbsentSettingForm(forms.ModelForm):
    class Meta:
        model = AbsentSetting
        fields = '__all__'

    def my_is_valid(self):
        self.full_clean()
        no_of_absent = self.cleaned_data.get('no_of_absent')

        if no_of_absent and no_of_absent < 0:
            return False
        return True


class LateSettingForm(forms.ModelForm):
    class Meta:
        model = LateSetting
        fields = '__all__'

    def my_is_valid(self):
        self.full_clean()
        late_grace_time = self.cleaned_data.get('late_grace_time')
        late_grace_time_unit = self.cleaned_data.get('late_grace_time_unit')
        late_last_time = self.cleaned_data.get('late_last_time')
        late_last_time_unit = self.cleaned_data.get('late_last_time_unit')

        if late_grace_time_unit == 'hour' and late_grace_time is not None:
            late_grace_time = late_grace_time * 60
        if late_last_time_unit == 'hour' and late_last_time is not None:
            late_last_time = late_last_time * 60

        if late_grace_time is not None and late_last_time is not None:
            if late_grace_time > late_last_time:
                return False
        return True


class LateSlabForm(forms.ModelForm):
    class Meta:
        model = LateSlab
        fields = '__all__'

    def my_is_valid(self):
        self.full_clean()
        time = self.cleaned_data.get('time')
        days_to_consider = self.cleaned_data.get('days_to_consider')

        if days_to_consider is None or time is None or time < 0:
            return False
        return True


class EarlyOutSettingForm(forms.ModelForm):
    class Meta:
        model = EarlyOutSetting
        fields = '__all__'


class EarlyOutSlabForm(forms.ModelForm):
    class Meta:
        model = EarlyOutSlab
        fields = '__all__'

    def my_is_valid(self):
        self.full_clean()
        time = self.cleaned_data.get('time')
        days_to_consider = self.cleaned_data.get('days_to_consider')

        if days_to_consider is None or time is None or time < 0:
            return False
        return True


class UnderWorkSlabForm(forms.ModelForm):
    class Meta:
        model = UnderWorkSlab
        fields = '__all__'

    def my_is_valid(self):
        self.full_clean()
        time = self.cleaned_data.get('time')
        days_to_consider = self.cleaned_data.get('days_to_consider')

        if days_to_consider is None or time is None or time <= 0:
            return False
        return True


class BonusGroupCreateForm(forms.ModelForm):
    yearly_component = forms.ModelMultipleChoiceField(
        BonusComponent.objects.filter(bonus_period='year'),
        required=False
    )
    half_yearly_component = forms.ModelMultipleChoiceField(
        BonusComponent.objects.filter(bonus_period='half-year'),
        required=False
    )
    quarterly_component = forms.ModelMultipleChoiceField(
        BonusComponent.objects.filter(bonus_period='quarter'),
        required=False
    )
    monthly_component = forms.ModelMultipleChoiceField(
        BonusComponent.objects.filter(bonus_period='month'),
        required=False
    )

    class Meta:
        model = BonusGroup
        fields = ('name', 'short_code', 'description', 'status')

        error_messages = {
            'title': {'required': 'Title field is required.'}
        }

    def my_is_valid(self):
        self.full_clean()
        name = self.cleaned_data.get('name')
        if not name:
            return False
        return True


class BonusComponentSettingsUpdateForm(forms.ModelForm):
    class Meta:
        model = BonusComponent
        fields = ('rule_type', 'bonus_period', 'bonus_frequency')

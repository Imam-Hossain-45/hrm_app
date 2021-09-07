from django import forms
from leave.models import *
from django.core.validators import EMPTY_VALUES
from django.forms.models import inlineformset_factory


def clean_unique(form, field, exclude_intial=True, format="The %(field)s %(value)s has already been taken."):
    value = form.cleaned_data.get(field)
    if value:
        qs = form._meta.model._default_manager.filter(**{field: value})
        if exclude_intial and form.initial:
            inital_value = form.initial.get(field)
            qs = qs.exclude(**{field: inital_value})
        if qs.count() > 0:
            raise forms.ValidationError(format % {'field': field, 'value': value})
        else:
            return value


class LeaveMasterForm(forms.ModelForm):
    gender = forms.ChoiceField(widget=forms.RadioSelect(),
                               choices=[('all', 'All'), ('male', 'Male'), ('female', 'Female')], initial='all')
    leave_credit_type = forms.ChoiceField(widget=forms.RadioSelect(),
                                          choices=[('fixed', 'Fixed'), ('timebase', 'Timebase')], initial='fixed')

    class Meta:
        model = LeaveMaster
        fields = '__all__'

    def clean_name(self):
        return clean_unique(self, 'name')

    def clean_short_name(self):
        return clean_unique(self, 'short_name')

    def clean(self):
        # validate the available frequency unit
        available_frequency_unit = self.cleaned_data.get('available_frequency_unit')

        # validate the available frequency
        if available_frequency_unit != 'lifetime':
            available_frequency_number = self.cleaned_data.get('available_frequency_number')
            if available_frequency_number in EMPTY_VALUES or available_frequency_number <= 0:
                self._errors['available_frequency_number'] = self.error_class(
                    ['Available Frequency will be greater than zero'])

        time_unit_basis = self.cleaned_data.get('time_unit_basis')
        if available_frequency_unit != time_unit_basis:
            if time_unit_basis == 'week' and available_frequency_unit not in ['week', 'month', 'year', 'quarter',
                                                                              'half_year', 'lifetime']:
                self._errors['available_frequency_unit'] = self.error_class(
                    ['Available Frequency unit will be week/month/year/quarter/half year/Lifetime.'])
            if time_unit_basis == 'month' and available_frequency_unit not in ['month', 'year', 'quarter',
                                                                               'half_year', 'lifetime']:
                self._errors['available_frequency_unit'] = self.error_class(
                    ['Available Frequency unit will be month/year/quarter/half year/Lifetime.'])

        # validate the carry forwardable
        carry_forwardable = self.cleaned_data.get('carry_forwardable')
        if carry_forwardable:
            if self.cleaned_data.get('carry_forward_on') in EMPTY_VALUES:
                self._errors['carry_forward_on'] = self.error_class(['This field is required'])
            else:
                if self.cleaned_data.get('carry_forward_on') == 'maximum_unit' and \
                        self.cleaned_data.get('carry_forward_leave_no') in EMPTY_VALUES:
                    self._errors['carry_forward_leave_no'] = self.error_class(['This field is required'])

        # validate the encashment
        encashable = self.cleaned_data.get('encashable')
        if encashable:
            if self.cleaned_data.get('encashment_on') in EMPTY_VALUES:
                self._errors['encashment_on'] = self.error_class(['This field is required'])
            else:
                if self.cleaned_data.get('encashment_on') == 'maximum_unit' and \
                        self.cleaned_data.get('encashment_leave_no') in EMPTY_VALUES:
                    self._errors['encashment_leave_no'] = self.error_class(['This field is required'])

        # validate the document required
        document_required = self.cleaned_data.get('document_required')
        if document_required:
            if self.cleaned_data.get('tolerance_limit') in EMPTY_VALUES:
                self._errors['tolerance_limit'] = self.error_class(['This field is required'])
        else:
            self.cleaned_data['tolerance_limit'] = None

        # validate the before_availing_leave
        before_availing_leave = self.cleaned_data.get('before_availing_leave')
        if before_availing_leave:
            if self.cleaned_data.get('before_minimum') in EMPTY_VALUES:
                self._errors['before_minimum'] = self.error_class(['This field is required'])
            if self.cleaned_data.get('before_maximum') in EMPTY_VALUES:
                self._errors['before_maximum'] = self.error_class(['This field is required'])

        # validate the before_availing_leave
        after_availing_leave = self.cleaned_data.get('after_availing_leave')
        if after_availing_leave:
            if self.cleaned_data.get('after_maximum') in EMPTY_VALUES:
                self._errors['after_maximum'] = self.error_class(['This field is required'])

        # validate the variable_with_time
        variable_with_time = self.cleaned_data.get('variable_with_time')
        if variable_with_time:
            if self.cleaned_data.get('round_of_time') in EMPTY_VALUES:
                self._errors['round_of_time'] = self.error_class(['This field is required'])
        else:
            self.cleaned_data['round_of_time'] = None

        # validate if time unit is hour, fractional will be checked
        if time_unit_basis == 'hour':
            if self.cleaned_data.get('fractional') is False:
                self._errors['fractional'] = self.error_class(['This field is required'])
        else:
            self.cleaned_data['fractional'] = False

        # validate the fractional
        fractional = self.cleaned_data.get('fractional')
        if fractional:
            if self.cleaned_data.get('fractional_time_unit') in EMPTY_VALUES:
                self._errors['fractional_time_unit'] = self.error_class(['This field is required'])
        else:
            self.cleaned_data['fractional_time_unit'] = ''
        return self.cleaned_data


class PartialLeaveConverterForm(forms.ModelForm):
    class Meta:
        model = PartialLeaveConverter
        fields = ('partial_leave_hours', 'partial_leave_day')

    def clean(self):
        if self.cleaned_data.get('partial_leave_hours') is not None:
            if self.cleaned_data.get('partial_leave_day') in EMPTY_VALUES:
                self._errors['partial_leave_day'] = self.error_class(['This field is required'])


class LeaveGroupForm(forms.ModelForm):
    leave = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           queryset=LeaveMaster.objects.filter(status=True),
                                           required=True, label='Select Leave(s) to create the Group')

    class Meta:
        model = LeaveGroup
        fields = '__all__'


class RadioSelectNotNull(forms.RadioSelect):
    """
    A widget which removes the default '-----' option from RadioSelect
    """

    def optgroups(self, name, value, attrs=None):
        """Return a list of optgroups for this widget."""
        if self.choices[0][0] == '':
            self.choices.pop(0)
        return super(RadioSelectNotNull, self).optgroups(name, value, attrs)


class LeaveSettingsForm(forms.ModelForm):
    timebase = forms.CharField(max_length=100)
    fraction = forms.CharField(max_length=100)

    class Meta:
        model = LeaveGroupSettings
        fields = ('employee_can_apply', 'leave_credit', 'minimum_enjoy', 'maximum_enjoy', 'leave_gap', 'minimum_gap',
                  'minimum_gap_unit', 'eligibility_based_on', 'eligible_employee_in', 'cannot_enjoy',
                  'cannot_enjoy_unit','avail_based_on', 'avail_employee_in', 'can_enjoy', 'can_enjoy_unit',
                  'timebase_credit', 'timebase_credit_unit', 'work_will_create', 'work_will_create_unit',
                  'fractional_duration')
        widgets = {
            'eligibility_based_on': forms.RadioSelect(),
            'eligible_employee_in': RadioSelectNotNull(),
            'avail_based_on': forms.RadioSelect(),
            'avail_employee_in': RadioSelectNotNull(),
        }

    def clean(self):
        # validate the Leave Gap
        if self.cleaned_data.get('leave_gap') is True:
            if self.cleaned_data.get('minimum_gap') in EMPTY_VALUES:
                self._errors['minimum_gap'] = self.error_class(['This field is required'])
        else:
            self.cleaned_data['minimum_gap'] = None

        # validate the eligibility
        eligibility = self.cleaned_data.get('eligibility_based_on')
        if eligibility == 'time_wise':
            self.cleaned_data['eligible_employee_in'] = None
            if self.cleaned_data.get('cannot_enjoy') in EMPTY_VALUES:
                self._errors['cannot_enjoy'] = self.error_class(['This field is required'])
        else:
            self.cleaned_data['cannot_enjoy'] = None
            if self.cleaned_data.get('eligible_employee_in') in EMPTY_VALUES:
                self._errors['eligible_employee_in'] = self.error_class(['This field is required'])

        # validate the avail capability
        avail = self.cleaned_data.get('avail_based_on')
        if avail == 'time_wise':
            self.cleaned_data['avail_employee_in'] = None
            if self.cleaned_data.get('can_enjoy') in EMPTY_VALUES:
                self._errors['can_enjoy'] = self.error_class(['This field is required'])
        else:
            self.cleaned_data['can_enjoy'] = None
            if self.cleaned_data.get('avail_employee_in') in EMPTY_VALUES:
                self._errors['avail_employee_in'] = self.error_class(['This field is required'])

        # validate the timebase_credit
        if self.cleaned_data.get('timebase') == 'timebase':
            timebase_credit = self.cleaned_data.get('timebase_credit')
            if timebase_credit in EMPTY_VALUES:
                self.errors['timebase_credit'] = self.error_class(['This is field is required'])

            # validate the work_will_create
            work_will_create = self.cleaned_data.get('work_will_create')
            if work_will_create in EMPTY_VALUES:
                self.errors['work_will_create'] = self.error_class(['This is field is required'])

        # validate the fractional_duration
        if self.cleaned_data.get('fraction') == "True":
            fractional_duration = self.cleaned_data.get('fractional_duration')
            if fractional_duration in EMPTY_VALUES:
                self.errors['fractional_duration'] = self.error_class(['This is field is required'])

        return self.cleaned_data


class LeaveRestrictionForm(forms.ModelForm):
    class Meta:
        model = LeaveRestriction
        fields = ('can_enjoy', 'within', 'within_unit')


RestrictionFormset = inlineformset_factory(LeaveGroupSettings, LeaveRestriction, form=LeaveRestrictionForm, extra=1,
                                           can_delete=True)

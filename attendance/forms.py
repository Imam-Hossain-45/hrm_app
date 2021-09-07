from django import forms
from attendance.models import ScheduleMaster, TimeTable, BreakTime, Days, HolidayGroup, HolidayMaster, TimeDuration, \
    FlexibleType, AttendanceData, AttendanceBreak, LateApplication, LateApprovalComment, EarlyApplication, \
    EarlyApprovalComment, CalendarMaster, ScheduleRecord, TimeTableRecord, BreakTimeRecord
from django.core.validators import EMPTY_VALUES
from setting.models import *
import datetime


# Update
class CalendarForm(forms.ModelForm):
    class Meta:
        model = CalendarMaster
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['parent_calendar'] = forms.ModelChoiceField(
                queryset=CalendarMaster.objects.all().exclude(id=self.instance.pk), required=False)

    def clean(self):
        effective_start_date = self.cleaned_data.get('effective_start_date')
        effective_end_date = self.cleaned_data.get('effective_end_date')
        if effective_start_date not in EMPTY_VALUES and effective_end_date not in EMPTY_VALUES:
            if effective_start_date > effective_end_date:
                self._errors['effective_end_date'] = self.error_class(['End date should be greater than start date.'])


class ScheduleMasterForm(forms.ModelForm):
    class Meta:
        model = ScheduleMaster
        fields = '__all__'
        exclude = ['days']
        widgets = {
            'days': forms.CheckboxSelectMultiple,
            'overtime_allowed': forms.CheckboxInput
        }
        labels = {
            'minimum_working_hour_per_day': 'Minimum',
            'minimum_working_hour_per_day_unit': 'Minimum',
            'maximum_working_hour_per_day': 'Maximum',
            'maximum_working_hour_per_day_unit': 'Maximum',
            'total_working_hour_per_day': 'Per Day',
            'total_working_hour_per_day_unit': 'Per Day',
            'total_working_hour_per_week': 'Per Week',
            'total_working_hour_per_week_unit': 'Per Week',
            'total_working_hour_per_month': 'Per Month',
            'total_working_hour_per_month_unit': 'Per Month'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['parent_schedule'] = forms.ModelChoiceField(
                queryset=ScheduleMaster.objects.all().exclude(id=self.instance.pk), required=False)

    def clean(self):
        schedule_type = self.cleaned_data.get('schedule_type')
        if schedule_type == 'roster':
            roster_type = self.cleaned_data.get('roster_type')
            if roster_type in EMPTY_VALUES:
                self._errors['roster_type'] = self.error_class(['This field is required.'])
        if self.instance:
            instance_id = ScheduleMaster.objects.filter(shortcode=self.cleaned_data.get('shortcode')).exclude(
                id=self.instance.id)
        else:
            instance_id = ScheduleMaster.objects.filter(shortcode=self.cleaned_data.get('shortcode'))
        if instance_id.exists():
            self._errors['shortcode'] = self.error_class(['This short code is already in use.'])


class ScheduleMasterTimeTableForm(forms.ModelForm):
    days = forms.ModelMultipleChoiceField(
        queryset=Days.objects,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = TimeTable
        fields = '__all__'
        exclude = ['days', 'schedule_master']


class ScheduleMasterBreakTimeForm(forms.ModelForm):
    class Meta:
        model = BreakTime
        fields = '__all__'
        labels = {
            'break_start': 'Break In',
            'break_end': 'Break Out'
        }


class ScheduleMasterTimeDurationForm(forms.ModelForm):
    class Meta:
        model = TimeDuration
        fields = '__all__'
        labels = {
            'break_start': 'Break In',
            'break_end': 'Break Out'
        }


class ScheduleMasterFlexibleTypeForm(forms.ModelForm):
    days = forms.ModelMultipleChoiceField(
        queryset=Days.objects,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = FlexibleType
        fields = '__all__'
        exclude = ['days', 'schedule_master']


class HolidayGroupCreateForm(forms.ModelForm):
    holiday = forms.ModelMultipleChoiceField(
        queryset=HolidayMaster.objects,
        required=False
    )

    class Meta:
        model = HolidayGroup
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


class DateInput(forms.DateInput):
    input_type = 'date'


class HolidayMasterCreateForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}),
                                 error_messages={'required': 'Start Date field is required.'})
    end_date = forms.CharField(widget=forms.DateInput(attrs={'type': 'date'}),
                               error_messages={'required': 'End Date field is required.'})

    class Meta:
        model = HolidayMaster
        fields = ('name', 'short_code', 'start_date', 'end_date', 'description', 'type', 'status')

        error_messages = {
            'title': {'required': 'Title field is required.'}
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = AttendanceData
        fields = ('employee', 'date', 'in_time', 'out_time', 'out_date')

    def clean(self):
        date = self.cleaned_data.get('date')
        out_date = self.cleaned_data.get('out_date')
        if date not in EMPTY_VALUES and out_date not in EMPTY_VALUES:
            if date > out_date:
                self._errors['out_date'] = self.error_class(['Out date should be greater than in date.'])


class AttendanceBreakForm(forms.ModelForm):
    class Meta:
        model = AttendanceBreak
        fields = ('break_start', 'break_start_date', 'break_end', 'break_end_date')

    def clean(self):
        break_start_date = self.cleaned_data.get('break_start_date')
        break_end_date = self.cleaned_data.get('break_end_date')
        if break_start_date not in EMPTY_VALUES and break_end_date not in EMPTY_VALUES:
            if break_start_date > break_end_date:
                self._errors['break_end_date'] = self.error_class(
                    ['Break end date should be greater than break start date.'])


class ActionAttendanceForm(forms.ModelForm):
    in_date = forms.DateField(required=False)

    class Meta:
        model = AttendanceData
        fields = ('in_time', 'out_time', 'out_date')

    def clean(self):
        in_date = self.cleaned_data.get('in_date')
        out_date = self.cleaned_data.get('out_date')
        if in_date not in EMPTY_VALUES and out_date not in EMPTY_VALUES:
            if in_date > out_date:
                self._errors['out_date'] = self.error_class(["Out date should be greater than in date."])


class LateEntryForm(forms.ModelForm):
    attendance = forms.CharField(error_messages={'required': 'Attendance is required for this date.'})
    entry_date = forms.DateField(initial=datetime.date.today)
    entry_time = forms.TimeField(required=False)

    class Meta:
        model = LateApplication
        fields = ('reason_of_late', 'attachment')

    def __init__(self, query, *args, **kwargs):
        self.query = query
        attendance_time = AttendanceData.objects.filter(employee_id=query, date=datetime.date.today()).last()
        if attendance_time:
            id = attendance_time.id
            in_time = attendance_time.in_time
        else:
            id = None
            in_time = None
        super().__init__(*args, **kwargs)
        self.fields['entry_time'].initial = in_time
        self.fields['entry_time'].disabled = True
        self.fields['attendance'].initial = id


class LateApprovalForm(forms.ModelForm):
    class Meta:
        model = LateApprovalComment
        fields = ('comment',)


class EarlyOutForm(forms.ModelForm):
    attendance = forms.CharField(error_messages={'required': 'Attendance is required for this date.'})
    entry_date = forms.DateField(initial=datetime.date.today)

    class Meta:
        model = EarlyApplication
        fields = ('early_out_time', 'reason_of_early_out', 'attachment')

    def __init__(self, query, *args, **kwargs):
        self.query = query
        attendance_time = AttendanceData.objects.filter(employee_id=query, date=datetime.date.today()).last()
        if attendance_time:
            id = attendance_time.id
            out_time = attendance_time.out_time
        else:
            id = None
            out_time = None
        super().__init__(*args, **kwargs)
        self.fields['early_out_time'].initial = out_time
        self.fields['attendance'].initial = id


class EarlyApprovalForm(forms.ModelForm):
    class Meta:
        model = EarlyApprovalComment
        fields = ('comment',)


class SchedulingForm(forms.ModelForm):
    class Meta:
        model = ScheduleRecord
        fields = ('is_working_day',)


class SchedulingTimetableForm(forms.ModelForm):
    class Meta:
        model = TimeTableRecord
        fields = ('in_time', 'out_time', 'out_date')


class SchedulingBreakForm(forms.ModelForm):
    class Meta:
        model = BreakTimeRecord
        fields = ('break_start', 'break_start_date', 'break_end', 'break_end_date')


class ActionSchedulingForm(forms.ModelForm):
    class Meta:
        model = TimeTableRecord
        fields = ('in_time', 'out_time', 'out_date')

    def clean(self):
        if self.cleaned_data.get('in_time') in EMPTY_VALUES:
            self._errors['in_time'] = self.error_class(
                ['This field is required.'])


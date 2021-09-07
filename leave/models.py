from django.db import models
from datetime import date, datetime
from helpers.models import Model
from .validators import validate_file_extension

unit_choice = [('day', 'Day'), ('week', 'Week'), ('month', 'Month'),
               ('year', 'Year'),
               ('quarter', 'Quarter'), ('half_year', 'Half Year'), ('lifetime', 'Lifetime')]
eligibility_choices = [('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year')]


def secondsToText(secs):
    days = secs // 86400
    hours = (secs - days * 86400) // 3600
    minutes = (secs - days * 86400 - hours * 3600) // 60
    seconds = secs - days * 86400 - hours * 3600 - minutes * 60
    result = ("{} day(s), ".format(int(days)) if days else "") + \
             ("{} hour(s), ".format(int(hours) if hours else "")) + \
              ("{} minute(s), ".format(int(minutes)) if minutes else "") + \
              ("{} second(s), ".format(int(seconds)) if seconds else "")

    return result


class LeaveMaster(Model):
    name = models.CharField(max_length=255, unique=True, null=True, verbose_name='Name of a Leave')
    short_name = models.CharField(max_length=255, unique=True, null=True, verbose_name='Leave Short Name')
    description = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=6, null=True, choices=[('all', 'All'), ('male', 'Male'), ('female', 'Female')],
                              default='all')
    available_frequency_number = models.DecimalField(max_digits=10, decimal_places=2, null=True,
                                                     default='0.0',
                                                     help_text="Leave available frequency")
    available_frequency_unit = models.CharField(max_length=50, null=True,
                                                choices=unit_choice,
                                                default='year', verbose_name='Available Frequency')
    time_unit_basis = models.CharField(max_length=50,
                                       choices=[('hour', 'Hour'), ('day', 'Day'), ('week', 'Week'), ('month', 'Month')],
                                       default='day',
                                       verbose_name="Select Time Unit of this leave")
    paid = models.BooleanField(default=True, blank=True, verbose_name='Paid Leave')
    carry_forwardable = models.BooleanField(default=False, blank=True,
                                            verbose_name='This leave is being Carry Forwardable')
    carry_forward_on = models.CharField(max_length=255, choices=[('accumulated_balance', 'Accumulated Balance'),
                                                                 ('maximum_unit', 'Maximum Unit')], blank=True,
                                        null=True)
    carry_forward_leave_no = models.IntegerField(blank=True, null=True)
    encashable = models.BooleanField(default=False, blank=True,
                                     verbose_name='This leave is being Encashable')
    encashment_on = models.CharField(max_length=255, choices=[('accumulated_balance', 'Accumulated Balance'),
                                                              ('maximum_unit', 'Maximum Unit')], blank=True,
                                     null=True)
    encashment_leave_no = models.IntegerField(blank=True, null=True)
    document_required = models.BooleanField(default=False, verbose_name='Documents Required when applying for leave')
    tolerance_limit = models.IntegerField(blank=True, null=True)
    tolerance_limit_unit = models.CharField(max_length=50,
                                            choices=[('hours', 'Hours'), ('days', 'Days'), ('months', 'Months')],
                                            default='days')
    before_availing_leave = models.BooleanField(default=False,
                                                verbose_name='Application required before availing leave')
    before_minimum = models.IntegerField(null=True, blank=True, verbose_name='Applying for leave before minimum')
    before_minimum_unit = models.CharField(max_length=10, blank=True, choices=[('hours', 'Hours'), ('days', 'Days'),
                                                                               ('months', 'Months')], default='days')
    before_maximum = models.IntegerField(null=True, blank=True, verbose_name='Applying for leave before maximum')
    before_maximum_unit = models.CharField(max_length=10, blank=True, choices=[('hours', 'Hours'), ('days', 'Days'),
                                                                               ('months', 'Months')], default='days')
    after_availing_leave = models.BooleanField(default=False,
                                               verbose_name='Can apply after availing leave')
    after_maximum = models.IntegerField(null=True, blank=True, verbose_name='Applying for leave within maximum')
    after_maximum_unit = models.CharField(max_length=10, blank=True, choices=[('hours', 'Hours'), ('days', 'Days'),
                                                                              ('months', 'Months')], default='days')

    leave_credit_type = models.CharField(max_length=10, choices=[('fixed', 'Fixed'), ('timebase', 'Timebase')],
                                         default='fixed', help_text="Earned leave")
    variable_with_time = models.BooleanField(default=False, verbose_name="Is the leave credit variable with time?")
    round_of_time = models.CharField(max_length=10, blank=True, null=True,
                                     choices=[('floor', 'Floor'), ('ceiling', 'Ceiling'), ('nearest', 'Nearest')],
                                     help_text="Round of time for timebase leave credit type")

    compensateable = models.BooleanField(default=False, help_text='Is the leave is compensateable with other leave?')

    partial_leave_allowed = models.BooleanField(default=False,
                                                help_text="Such a kind of leave that can be break within a day.")
    fractional = models.BooleanField(default=False, verbose_name='It a hourly Leave',
                                     help_text='Leave - that is a part of a day.')
    fractional_time_unit = models.CharField(max_length=20, blank=True, null=True,
                                            choices=[('minutes', 'Minutes'), ('hours', 'Hours')],
                                            verbose_name='Time unit for hourly leave')

    sandwich_leave_allowed = models.BooleanField(default=False)
    status = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return self.name


class PartialLeaveConverter(models.Model):
    leave = models.ForeignKey(LeaveMaster, on_delete=models.CASCADE, related_name='partial_leave',
                              related_query_name='partial_leave')
    partial_leave_hours = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, )
    partial_leave_day = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, )

    def __str__(self):
        return self.leave


class LeaveGroup(Model):
    leave = models.ManyToManyField(LeaveMaster, verbose_name='Select Leave(s) to create the Group',
                                   related_name='get_leave', related_query_name='get_leave')
    name = models.CharField(max_length=60, unique=True, null=True, verbose_name='Leave Group Name')
    code = models.CharField(max_length=255, unique=True, null=True, verbose_name='Short Code')
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return self.name


class LeaveGroupSettings(Model):
    leave_group = models.ForeignKey(LeaveGroup, on_delete=models.CASCADE, null=True, related_name='group_settings')
    leave_name = models.ForeignKey(LeaveMaster, on_delete=models.CASCADE, null=True, related_name='leave_settings')
    employee_can_apply = models.BooleanField(default=False)
    leave_credit = models.IntegerField(null=True)
    minimum_enjoy = models.IntegerField(blank=True, null=True)
    maximum_enjoy = models.IntegerField(blank=True, null=True)
    leave_gap = models.BooleanField(default=False, verbose_name='Leave Gap restriction allowed')
    minimum_gap = models.IntegerField(blank=True, null=True)
    minimum_gap_unit = models.CharField(null=True, max_length=20, choices=eligibility_choices, default='day')
    eligibility_based_on = models.CharField(
        choices=[('job_status_wise', 'Job Status wise'), ('time_wise', 'Time wise')], default='job_status_wise',
        max_length=50, null=True)
    eligible_employee_in = models.CharField(
        choices=[('probation_period', 'Probation Period'), ('confirmed_stage', 'Confirmed Stage')],
        max_length=50, blank=True, default=None, null=True, verbose_name='When employee is in')
    cannot_enjoy = models.IntegerField(blank=True, null=True, verbose_name='Employee cannot enjoy this leave within')
    cannot_enjoy_unit = models.CharField(null=True, max_length=20, choices=eligibility_choices, default='day')
    avail_based_on = models.CharField(
        choices=[('job_status_wise', 'Job Status wise'), ('time_wise', 'Time wise')], default='job_status_wise',
        max_length=50, null=True, verbose_name='Leave avail capability based on')
    avail_employee_in = models.CharField(
        choices=[('probation_period', 'Probation Period'), ('confirmed_stage', 'Confirmed Stage')],
        max_length=50, blank=True, default=None, null=True, verbose_name='When employee is in')
    can_enjoy = models.IntegerField(blank=True, null=True, verbose_name='Employee can enjoy this after')
    can_enjoy_unit = models.CharField(null=True, max_length=20, choices=eligibility_choices, default='day')
    timebase_credit = models.IntegerField(null=True, blank=True, verbose_name='For Time-based leave credit type')
    timebase_credit_unit = models.CharField(null=True, blank=True, max_length=20, choices=eligibility_choices,
                                            default='month')
    work_will_create = models.IntegerField(null=True, blank=True)
    work_will_create_unit = models.CharField(blank=True, null=True, max_length=20, choices=eligibility_choices,
                                             default='day')
    fractional_duration = models.IntegerField(blank=True, verbose_name='Leave Duration', default=0)

    def __str__(self):
        return "{} {}".format(self.leave_group, self.leave_name)


class LeaveRestriction(Model):
    leave_settings = models.ForeignKey(LeaveGroupSettings, on_delete=models.CASCADE, null=True,
                                       related_name='leave_restriction')
    can_enjoy = models.IntegerField(null=True)
    within = models.IntegerField(null=True)
    within_unit = models.CharField(choices=unit_choice, max_length=50, default='year')

    def __str__(self):
        return self.leave_settings


class LeaveEntry(Model):
    employee = models.ForeignKey('employees.EmployeeIdentification', on_delete=models.CASCADE, null=True, related_name='employee_name')
    leave_type = models.ForeignKey(LeaveMaster, on_delete=models.CASCADE, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    reason_of_leave = models.TextField(null=True, blank=True)
    attachment = models.FileField(upload_to='leave/', blank=True, null=True, validators=[validate_file_extension])
    status = models.CharField(max_length=100,
                              choices=[('pending', 'Pending'), ('declined', 'Declined'), ('approved', 'Approved')],
                              default='pending', blank=True, null=True)

    def __str__(self):
        return "{} {}".format(self.employee, self.leave_type)

    def duration(self):
        if self.leave_type.time_unit_basis == 'hour':
            delta = datetime.combine(self.end_date, self.end_time) - datetime.combine(self.start_date, self.start_time)
            return secondsToText(delta.total_seconds()).rstrip(", ")

        elif self.leave_type.time_unit_basis == 'day':
            delta = self.end_date - self.start_date
            return str(delta.days + 1) + ' day(s)'


class LeaveAvail(Model):
    employee = models.ForeignKey('employees.EmployeeIdentification', on_delete=models.CASCADE, null=True)
    avail_leave = models.ForeignKey(LeaveMaster, on_delete=models.SET_NULL, null=True, blank=True)
    credit_seconds = models.IntegerField(null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return "{} {}".format(self.employee, self.avail_leave)


class LeaveRemaining(Model):
    employee = models.ForeignKey('employees.EmployeeIdentification', on_delete=models.CASCADE, null=True)
    leave = models.ForeignKey(LeaveMaster, on_delete=models.CASCADE, null=True, blank=True)
    remaining_in_seconds = models.IntegerField(blank=True, null=True)
    availing_in_seconds = models.IntegerField(default=0)
    leave_expired_date = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(default=True)


class LeaveApprovalComment(Model):
    user = models.ForeignKey('user_management.User', on_delete=models.CASCADE, null=True)
    leave_entry = models.ForeignKey(LeaveEntry, on_delete=models.CASCADE, null=True, related_name='leave_entry')
    comment = models.TextField(null=True)

    def __str__(self):
        return "{} {}".format(self.user, self.leave_entry)

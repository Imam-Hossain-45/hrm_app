from django.db import models
from helpers.models import Model
from employees.models import EmployeeIdentification
from leave.validators import validate_file_extension
from leave.models import LeaveMaster


class AttendanceData(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True,
                                 related_name='employee_daily_attendance')
    date = models.DateField(null=True)
    in_time = models.TimeField(null=True, blank=True)
    out_time = models.TimeField(null=True, blank=True)
    out_date = models.DateField(null=True, blank=True)


class AttendanceBreak(Model):
    attendance = models.ForeignKey(AttendanceData, on_delete=models.CASCADE, null=True)
    break_start = models.TimeField(blank=True, null=True)
    break_start_date = models.DateField(blank=True, null=True)
    break_end = models.TimeField(blank=True, null=True)
    break_end_date = models.DateField(blank=True, null=True)


class LateApplication(Model):
    attendance = models.ForeignKey(AttendanceData, on_delete=models.CASCADE, null=True)
    reason_of_late = models.TextField()
    attachment = models.FileField(upload_to='late_entry/', blank=True, null=True, validators=[validate_file_extension])
    status = models.CharField(max_length=100,
                              choices=[('pending', 'Pending'), ('declined', 'Declined'), ('approved', 'Approved')],
                              default='pending', blank=True, null=True)


class LateApprovalComment(Model):
    user = models.ForeignKey('user_management.User', on_delete=models.CASCADE, null=True)
    late_entry = models.ForeignKey(LateApplication, on_delete=models.CASCADE, null=True, related_name='late_entry')
    comment = models.TextField(null=True)

    def __str__(self):
        return "{} {}".format(self.user, self.late_entry)


class EarlyApplication(Model):
    attendance = models.ForeignKey(AttendanceData, on_delete=models.CASCADE, null=True)
    early_out_time = models.TimeField(null=True)
    reason_of_early_out = models.TextField(null=True)
    attachment = models.FileField(upload_to='early_out/', blank=True, null=True, validators=[validate_file_extension])
    status = models.CharField(max_length=100,
                              choices=[('pending', 'Pending'), ('declined', 'Declined'), ('approved', 'Approved')],
                              default='pending', blank=True, null=True)


class EarlyApprovalComment(Model):
    user = models.ForeignKey('user_management.User', on_delete=models.CASCADE, null=True)
    early_out = models.ForeignKey(EarlyApplication, on_delete=models.CASCADE, null=True, related_name='early_out')
    comment = models.TextField(null=True)

    def __str__(self):
        return "{} {}".format(self.user, self.early_out)


class ScheduleRecord(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True,
                                 related_name='employee_daily_record')
    date = models.DateField(null=True)
    is_weekend = models.BooleanField(default=False)
    is_holiday = models.BooleanField(default=False)
    is_working_day = models.BooleanField(default=True)
    is_leave = models.BooleanField(default=False)
    working_hour = models.IntegerField(default=0, blank=True)
    working_hour_unit = models.CharField(max_length=8, null=True, blank=True)


class TimeTableRecord(Model):
    """Model to hold in and out time based on date of schedule."""

    schedule_record = models.OneToOneField(ScheduleRecord, blank=True, on_delete=models.CASCADE,
                                           related_name='timetable_record_model', null=True)
    in_time = models.TimeField(blank=True, null=True)
    out_time = models.TimeField(blank=True, null=True)
    out_date = models.DateField(null=True, blank=True)


class BreakTimeRecord(Model):
    """Model to hold multiple break times based on timetable record."""

    timetable_record = models.ForeignKey(TimeTableRecord, on_delete=models.CASCADE, null=True)
    break_start = models.TimeField(null=True, blank=True)
    break_start_date = models.DateField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)
    break_end_date = models.DateField(null=True, blank=True)


class DailyRecord(Model):
    schedule_record = models.OneToOneField(ScheduleRecord, on_delete=models.CASCADE, blank=True, null=True)
    daily_working_seconds = models.IntegerField(default=0)
    is_overtime = models.BooleanField(default=False)
    daily_pre_overtime_seconds = models.IntegerField(default=0)
    daily_post_overtime_seconds = models.IntegerField(default=0)
    late = models.BooleanField(default=False)
    late_value = models.IntegerField(default=0)
    early = models.BooleanField(default=False)
    early_out_value = models.IntegerField(default=0)
    under_work = models.BooleanField(default=False)
    under_work_value = models.IntegerField(default=0)
    is_present = models.BooleanField(default=False)
    is_leave_paid = models.BooleanField(default=False)
    leave_master = models.ForeignKey(LeaveMaster, on_delete=models.SET_NULL, null=True)
    countable_pre_overtime = models.IntegerField(default=0)
    countable_post_overtime = models.IntegerField(default=0)

from django.db import models
from helpers.models import Model
from django.core.exceptions import ValidationError


class Days(Model):
    """Model to hold 7 days."""

    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class ScheduleMaster(Model):
    """Actual model for Schedule master data."""

    SCHEDULE_TYPE_CHOICES = (
        ('regular-fixed-time', 'Regular Fixed Time'),
        ('fixed-day', 'Fixed Day'),
        ('hourly', 'Hourly'),
        ('weekly', 'Weekly'),
        ('day', 'Day'),
        ('freelancing', 'Freelancing'),
        ('roster', 'Roster'),
        ('flexible', 'Flexible'),
    )
    ROSTER_TYPE_CHOICES = (
        ('fixed-roster', 'Fixed Roster'),
        ('variable-roster', 'Variable Roster')
    )
    TIME_CHOICES = (
        ('hour', 'Hour'),
        ('minute', 'Minute')
    )

    parent_schedule = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True,
                                        limit_choices_to={'status': True})
    name = models.CharField(max_length=255)
    shortcode = models.CharField(max_length=255, null=True, unique=True)
    description = models.TextField(blank=True, null=True)
    schedule_type = models.CharField(max_length=255, choices=SCHEDULE_TYPE_CHOICES, null=True)
    roster_type = models.CharField(max_length=255, choices=ROSTER_TYPE_CHOICES, blank=True, null=True)
    days = models.ManyToManyField(Days, through='TimeTable')
    minimum_working_hour_per_day = models.IntegerField(blank=True, default=0)
    minimum_working_hour_per_day_unit = models.CharField(max_length=10, choices=TIME_CHOICES, blank=True,
                                                         default='hour')
    maximum_working_hour_per_day = models.IntegerField(blank=True, default=0)
    maximum_working_hour_per_day_unit = models.CharField(max_length=10, choices=TIME_CHOICES, blank=True,
                                                         default='hour')
    total_working_hour_per_day = models.IntegerField(blank=True, default=0)
    total_working_hour_per_day_unit = models.CharField(max_length=10, choices=TIME_CHOICES, blank=True, default='hour')
    total_working_hour_per_week = models.IntegerField(blank=True, default=0)
    total_working_hour_per_week_unit = models.CharField(max_length=10, choices=TIME_CHOICES, blank=True, default='hour')
    total_working_hour_per_month = models.IntegerField(blank=True, default=0)
    total_working_hour_per_month_unit = models.CharField(max_length=10, choices=TIME_CHOICES, blank=True,
                                                         default='hour')
    working_day = models.IntegerField(blank=True, default=0)
    vacation = models.IntegerField(blank=True, default=0)
    status = models.BooleanField(default=True, blank=True)

    def save(self, *args, **kwargs):
        if self.parent_schedule and self.parent_schedule.name == self.name:
            raise ValidationError('Schedule can\'t have itself as a parent!')
        return super(ScheduleMaster, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class TimeTable(Model):
    """Model to hold in and out time based on days."""

    days = models.ForeignKey(Days, on_delete=models.CASCADE)
    schedule_master = models.ForeignKey(ScheduleMaster, blank=True, on_delete=models.CASCADE,
                                        related_name='timetable_model')
    in_time = models.TimeField(blank=True, null=True)
    out_time = models.TimeField(blank=True, null=True)


class TimeDuration(Model):
    """Model to hold Hourly Schedule Type."""

    timetable = models.ForeignKey(TimeTable, on_delete=models.CASCADE, null=True)
    work_start = models.TimeField()
    work_end = models.TimeField()
    break_start = models.TimeField()
    break_end = models.TimeField()


class BreakTime(Model):
    """Model to hold multiple break times."""

    timetable = models.ForeignKey(TimeTable, on_delete=models.CASCADE, null=True, related_name='breaktime_model')
    break_start = models.TimeField()
    break_end = models.TimeField()


class FlexibleType(Model):
    """Model to hold Flexible Schedule Type."""

    TIME_CHOICES = (
        ('hour', 'Hour'),
        ('minute', 'Minute')
    )

    days = models.ForeignKey(Days, on_delete=models.CASCADE)
    schedule_master = models.ForeignKey(ScheduleMaster, blank=True, on_delete=models.CASCADE,
                                        related_name='flexible_schedule')
    working_hour = models.IntegerField(blank=True, default=0)
    working_hour_unit = models.CharField(max_length=10, choices=TIME_CHOICES, blank=True, default='hour')

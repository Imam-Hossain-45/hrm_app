from django.db import models
from helpers.models import Model
from multiselectfield import MultiSelectField
from .holiday_master import HolidayGroup
from django.core.exceptions import ValidationError

DAYS_OF_WEEK = (
    (1, 'Monday'),
    (2, 'Tuesday'),
    (3, 'Wednesday'),
    (4, 'Thursday'),
    (5, 'Friday'),
    (6, 'Saturday'),
    (7, 'Sunday'),
)


class CalendarMaster(Model):
    parent_calendar = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True,
                                        limit_choices_to={'status': True})
    name = models.CharField(max_length=255, unique=True)
    shortcode = models.CharField(max_length=255, null=True, unique=True)
    description = models.TextField(blank=True, null=True)
    effective_start_date = models.DateField()
    effective_end_date = models.DateField(blank=True)
    workday = MultiSelectField(choices=DAYS_OF_WEEK, blank=True, null=True)
    holiday_group = models.ForeignKey(HolidayGroup, on_delete=models.SET_NULL, blank=True, null=True,
                                      verbose_name="Select Holiday Group", limit_choices_to={'status': True})
    status = models.BooleanField(default=True, blank=True)

    def save(self, *args, **kwargs):
        if self.parent_calendar and self.parent_calendar.name == self.name:
            raise ValidationError('Calendar can\'t have itself as a parent!')
        return super(CalendarMaster, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

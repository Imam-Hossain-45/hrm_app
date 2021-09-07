from django.db import models
from helpers.models import Model


class WorkDaySchedule(Model):
    total_day_of_month = models.DecimalField(max_digits=10, decimal_places=2, default=30)
    total_working_day_of_month = models.DecimalField(max_digits=10, decimal_places=2, default=30)
    total_day_of_week = models.DecimalField(max_digits=10, decimal_places=2, default=7)
    total_working_day_of_week = models.DecimalField(max_digits=10, decimal_places=2, default=30)
    total_day_of_year = models.DecimalField(max_digits=10, decimal_places=2, default=365)
    total_working_day_of_year = models.DecimalField(max_digits=10, decimal_places=2, default=30)
    start_day_of_month = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    end_day_of_month = models.DecimalField(max_digits=10, decimal_places=2, default=30)

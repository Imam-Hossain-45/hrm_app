from django.db import models
from helpers.models import Model


class HolidayMaster(Model):
    name = models.CharField(max_length=255)
    short_code = models.CharField(max_length=20, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=[
        ('festival', 'Festival'),
        ('national', 'National'),
        ('international', 'International')
    ], default='festival')

    status = models.BooleanField(default=True, blank=True)

    def __str__(self):
        if self.short_code:
            return "{} - {}".format(self.short_code.upper(), self.name)
        else:
            return "{} - {}".format('', self.name)


class HolidayGroup(Model):
    holiday = models.ManyToManyField(HolidayMaster, through='HolidayGroupMasterMembers')
    name = models.CharField(max_length=255)
    short_code = models.CharField(max_length=20, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True, blank=True)

    def __str__(self):
        if self.short_code:
            return "{} - {}".format(self.short_code.upper(), self.name)
        else:
            return "{} - {}".format('', self.name)


class HolidayGroupMasterMembers(Model):
    group = models.ForeignKey(HolidayGroup, on_delete=models.CASCADE)
    master = models.ForeignKey(HolidayMaster, on_delete=models.CASCADE)

from django.db import models
from helpers.models import Model


class PayGrade(Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    status = models.BooleanField(default=True, blank=True)
    description = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey('user_management.User', blank=True, null=True, on_delete=models.SET_NULL,
                                   related_name='grade_created_by')
    updated_by = models.ForeignKey('user_management.User', blank=True, null=True, on_delete=models.SET_NULL,
                                   related_name='grade_updated_by')

    def __str__(self):
        return str(self.name)


class PayScale(Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    max_range = models.FloatField(blank=False, default=0.00)
    min_range = models.FloatField(blank=False, default=0.00)
    status = models.BooleanField(default=True, blank=True)
    description = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey('user_management.User', blank=True, null=True, on_delete=models.SET_NULL,
                                   related_name='pay_scale_created_by')
    updated_by = models.ForeignKey('user_management.User', blank=True, null=True, on_delete=models.SET_NULL,
                                   related_name='pay_scale_updated_by')

    def __str__(self):
        return str(self.name)

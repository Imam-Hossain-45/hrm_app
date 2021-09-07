from django.db import models
from helpers.models import Model


STATUS_CHOICE = (
    ('active', 'Active'),
    ('inactive', 'Inactive')
)


class EmploymentType(Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = 'Employment Types'


class JobStatus(Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = 'Job Status'


class Bank(Model):
    name = models.CharField(max_length=255, blank=True, null=False, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='active')

    def __str__(self):
        return str(self.name)

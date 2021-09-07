from django.db import models
from helpers.models import Model


class Countries(Model):
    code = models.CharField(max_length=11, blank=True, null=True)
    name = models.CharField(max_length=255, null=True)
    dial_code = models.CharField(max_length=255, null=True)
    currency = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name


class States(Model):
    country = models.ForeignKey(Countries, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name


class Cities(Model):
    state = models.ForeignKey(States, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name

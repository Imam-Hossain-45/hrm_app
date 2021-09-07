from django.contrib import admin

from . import models

admin.site.register(models.Branch)
admin.site.register(models.Bank)
admin.site.register(models.Countries)
admin.site.register(models.States)
admin.site.register(models.Cities)
admin.site.register(models.EmploymentType)
admin.site.register(models.JobStatus)

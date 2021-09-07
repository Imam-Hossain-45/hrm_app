from django.contrib import admin

from . import models

admin.site.register(models.Component)
admin.site.register(models.PayGrade)
admin.site.register(models.PayScale)

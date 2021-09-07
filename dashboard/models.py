from django.db import models
from helpers.models import Model

# Create your models here.


class NoticeBoard(Model):
    NOTICE_TYPE_CHOICES = (
        ('custom', 'Custom'),
        ('calendar', 'Calendar'),
        ('birthday', 'Birthday'),
    )

    user = models.ForeignKey('user_management.User', on_delete=models.CASCADE)
    # custom = models.ForeignKey(CustomNotice, on_delete=models.CASCADE)
    holiday_id = models.IntegerField(blank=True, null=True)
    notice = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    published_datetime = models.DateTimeField(blank=True, null=True)
    type = models.CharField(
        max_length=11,
        default='calendar',
        choices=NOTICE_TYPE_CHOICES,
        blank=True
    )

    def __str__(self):
        return self.notice

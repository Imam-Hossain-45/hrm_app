from cimbolic.models import Variable
from django.db import models
from helpers.models import Model


STATUS_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive')
)


class BonusComponent(Model):
    BONUS_PERIOD_CHOICES = (
        ('year', 'Year'),
        ('half-year', 'Half Year'),
        ('quarter', 'Quarter'),
        ('month', 'Month'),
    )
    RULE_TYPE_CHOICES = (
        ('rule-based', 'Rule Based'),
        ('variable', 'Variable'),
    )

    name = models.CharField(max_length=50)
    short_code = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    variable = models.OneToOneField(
        Variable,
        on_delete=models.SET_NULL,
        related_name='+',
        editable=False,
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    bonus_period = models.CharField(
        max_length=20,
        choices=BONUS_PERIOD_CHOICES,
        default='year'
    )
    bonus_frequency = models.IntegerField(blank=True, null=True)
    rule_type = models.CharField(
        max_length=20, blank=True,
        choices=RULE_TYPE_CHOICES,
        default='rule-based'
    )

    def __str__(self):
        if self.short_code:
            return "{} - {}".format(self.short_code.upper(), self.name)
        else:
            return "{} - {}".format('', self.name)

    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)
            var = Variable.objects.create(
                name='BonusComponent_{}'.format(self.short_code),
                related_data_type=Variable.MODEL_INSTANCE_TYPE,
                related_data_path='payroll.BonusComponent.{}'.format(self.pk),
            )
            self.variable = var
            self.save()
        else:
            super().save(*args, **kwargs)


class BonusGroup(Model):
    bonus_component = models.ManyToManyField(BonusComponent, through='BonusGroupComponentMembers')
    name = models.CharField(max_length=255)
    short_code = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True, blank=True)

    def __str__(self):
        if self.short_code:
            return "{} - {}".format(self.short_code.upper(), self.name)
        else:
            return "{} - {}".format('', self.name)


class BonusGroupComponentMembers(Model):
    group = models.ForeignKey(BonusGroup, on_delete=models.CASCADE)
    component = models.ForeignKey(BonusComponent, on_delete=models.CASCADE)

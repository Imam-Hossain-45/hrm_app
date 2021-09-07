__all__ = [
    'OvertimeRule',
    'OvertimeDurationRestriction',
    'OvertimeWageCalculationFixedRate',
    'OvertimeWageCalculationRuleBased',
    'OvertimeWageCalculationVariable',
    'OvertimeWageCalculationManual',
]

from cimbolic.models import Variable
from django.db import models

from helpers.models import Model


class OvertimeRule(Model):
    """Model governing overtime rules."""
    SEGMENT_CHOICES = [
        ('pre', 'Pre-work Overtime'),
        ('post', 'Post-work Overtime'),
        ('both', 'Both'),
    ]

    DURATION_UNIT_CHOICES = [
        ('m', 'Minute(s)'),
        ('h', 'Hour(s)'),
    ]

    name = models.CharField(
        'rule name',
        max_length=200,
        unique=True,
    )
    code = models.CharField(
        'short code',
        max_length=20,
        unique=True,
    )
    description = models.CharField(
        max_length=250,
        blank=True,
    )

    default_calculation_unit = models.CharField(
        choices=DURATION_UNIT_CHOICES,
        default='m',
        max_length=1,
    )

    segment = models.CharField(
        'OT segment',
        choices=SEGMENT_CHOICES,
        default='post',
        max_length=4,
    )

    buffer_duration_pre = models.PositiveIntegerField(
        help_text='Minimum duration before overtime takes effect',
        default=0,
    )
    buffer_duration_unit_pre = models.CharField(
        choices=DURATION_UNIT_CHOICES,
        default='m',
        max_length=1,
    )

    minimum_working_duration_pre = models.PositiveIntegerField(
        help_text='Minimum duration to work for overtime to count',
        default=1,
    )
    minimum_working_duration_unit_pre = models.CharField(
        choices=DURATION_UNIT_CHOICES,
        default='h',
        max_length=1,
    )

    tolerance_time_pre = models.PositiveIntegerField(
        help_text='Helper for rounding the OT duration',
        default=0,
    )

    buffer_duration_post = models.PositiveIntegerField(
        help_text='Minimum duration before overtime takes effect',
        default=0,
    )
    buffer_duration_unit_post = models.CharField(
        choices=DURATION_UNIT_CHOICES,
        default='m',
        max_length=1,
    )

    minimum_working_duration_post = models.PositiveIntegerField(
        help_text='Minimum duration to work for overtime to count',
        default=1,
    )
    minimum_working_duration_unit_post = models.CharField(
        choices=DURATION_UNIT_CHOICES,
        default='h',
        max_length=1,
    )

    tolerance_time_post = models.PositiveIntegerField(
        help_text='Helper for rounding the OT duration',
        default=0,
    )

    taxable = models.BooleanField(
        help_text='Whether the overtime wage is taxable',
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk is not None:
            if self.count_enabled_wage_calculation_methods() != 1:
                raise ValueError('Exactly 1 wage calculation method must be active')
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
            OvertimeWageCalculationFixedRate.objects.create(rule=self)
            OvertimeWageCalculationVariable.objects.create(rule=self)
            OvertimeWageCalculationManual.objects.create(rule=self)
            OvertimeWageCalculationRuleBased.objects.create(rule=self)

    def count_enabled_wage_calculation_methods(self):
        """Return the number of wage calculation methods that are enabled."""
        return (
            self.fixed_rate_wage.enabled
            + self.variable_wage.enabled
            + self.manual_wage.enabled
            + self.rule_based_wage.enabled
        )

    @property
    def active_wage_calculation_model(self):
        """Return the name of the enabled wage calculation model."""
        if self.count_enabled_wage_calculation_methods() != 1:
            raise ValueError('Exactly 1 wage calculation method must be active')
        if self.fixed_rate_wage.enabled:
            return self.fixed_rate_wage
        elif self.variable_wage.enabled:
            return self.variable_wage
        elif self.manual_wage.enabled:
            return self.manual_wage
        elif self.rule_based_wage.enabled:
            return self.rule_based_wage


class OvertimeDurationRestriction(Model):
    """Model governing maximum overtime duration restrictions per rule."""
    SEGMENT_CHOICES = [
        ('pre', 'For Pre-work Overtime'),
        ('post', 'For Post-work Overtime'),
    ]

    SCOPE_UNIT_CHOICES = [
        ('d', 'Day(s)'),
        ('w', 'Week(s)'),
        ('m', 'Month(s)'),
    ]

    DURATION_UNIT_CHOICES = [
        ('m', 'Minute(s)'),
        ('h', 'Hour(s)'),
        ('d', 'Day(s)'),
        ('w', 'Week(s)')
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    rule = models.ForeignKey(
        OvertimeRule,
        on_delete=models.CASCADE,
        related_name='duration_restrictions',
        related_query_name='duration_restriction',
        null=True,
    )
    ot_segment = models.CharField(
        'OT segment',
        choices=SEGMENT_CHOICES,
        default='post',
        max_length=4,
    )
    scope_value = models.PositiveIntegerField(
        help_text='Time period (scope) in which the restriction applies',
    )
    scope_unit = models.CharField(
        help_text='Unit of measurement of the scope (time period)',
        choices=SCOPE_UNIT_CHOICES,
        max_length=1,
    )
    maximum_duration = models.PositiveIntegerField(
        help_text='Maximum duration of OT allowed',
    )
    maximum_duration_unit = models.CharField(
        help_text='Unit of duration',
        choices=DURATION_UNIT_CHOICES,
        max_length=1,
    )
    status = models.CharField(
        choices=STATUS_CHOICES,
        default='active',
        max_length=10,
    )

    def __str__(self):
        return '{} ({}) > every {} {}'.format(
            self.rule,
            self.ot_segment,
            self.scope_value,
            self.get_scope_unit_display().lower()
        )


class OvertimeWageCalculationFixedRate(Model):
    """Model governing fixed rate OT wage calculation."""
    method = 'fixed-rate'

    BASIS_CHOICES = [
        ('m', 'Minutely'),
        ('h', 'Hourly'),
        ('d', 'Daily'),
        ('s', 'Top of salary'),
    ]

    rule = models.OneToOneField(
        OvertimeRule,
        on_delete=models.CASCADE,
        related_name='fixed_rate_wage'
    )
    enabled = models.BooleanField(
        help_text='Whether this method is enabled',
        default=False,
    )
    basis = models.CharField(
        help_text='Scope type of the wage calculation (per hour, per day etc.)',
        choices=BASIS_CHOICES,
        default='h',
        max_length=1,
    )
    scope_value = models.PositiveIntegerField(
        help_text='Scope value (per how many hours/days)',
        default=1,
        blank=True,
    )
    amount = models.DecimalField(
        help_text='Fixed-rate amount',
        decimal_places=2,
        max_digits=10,
        blank=True,
        null=True,
    )

    def __str__(self):
        return (
            '{}, {}'
            .format(self.method.capitalize(), self.get_basis_display())
        )


class OvertimeWageCalculationRuleBased(Model):
    """Model governing rule based OT wage calculation."""
    method = 'rule-based'

    BASIS_CHOICES = [
        ('m', 'Minutely'),
        ('h', 'Hourly'),
        ('d', 'Daily'),
        ('s', 'Top of salary'),
    ]

    rule = models.OneToOneField(
        OvertimeRule,
        on_delete=models.CASCADE,
        related_name='rule_based_wage'
    )
    enabled = models.BooleanField(
        help_text='Whether this method is enabled',
        default=False,
    )
    basis = models.CharField(
        help_text='Scope type of the wage calculation (per hour, per day etc.)',
        choices=BASIS_CHOICES,
        default='h',
        max_length=1,
    )
    variable = models.OneToOneField(
        Variable,
        on_delete=models.SET_NULL,
        related_name='+',
        editable=False,
        null=True,
    )

    def __str__(self):
        return (
            '{}, {}'
            .format(self.method.capitalize(), self.get_basis_display())
        )

    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)
            var = Variable.objects.create(
                name='OvertimeRule_{}'.format(self.rule.code),
                related_data_type=Variable.MODEL_INSTANCE_TYPE,
                related_data_path='attendance.OvertimeWageCalculationRuleBased.{}'.format(self.pk),
            )
            self.variable = var
            self.save()
        else:
            super().save(*args, **kwargs)


class OvertimeWageCalculationVariable(Model):
    """Model governing variable OT wage calculation (from salary component)."""
    method = 'variable'

    BASIS_CHOICES = [
        ('m', 'Minutely'),
        ('h', 'Hourly'),
        ('d', 'Daily'),
        ('s', 'Top of salary'),
    ]

    rule = models.OneToOneField(
        OvertimeRule,
        on_delete=models.CASCADE,
        related_name='variable_wage'
    )
    enabled = models.BooleanField(
        help_text='Whether this method is enabled',
        default=False,
    )
    basis = models.CharField(
        help_text='Scope type of the wage calculation (per hour, per day etc.)',
        choices=BASIS_CHOICES,
        default='h',
        max_length=1,
    )

    def __str__(self):
        return (
            '{}, {}'
            .format(self.method.capitalize(), self.get_basis_display())
        )


class OvertimeWageCalculationManual(Model):
    """Model governing manual OT wage specification."""
    method = 'manual'

    rule = models.OneToOneField(
        OvertimeRule,
        on_delete=models.CASCADE,
        related_name='manual_wage'
    )
    enabled = models.BooleanField(
        help_text='Whether this method is enabled',
        default=False,
    )

    def __str__(self):
        return (
            '{}'
            .format(self.method.capitalize())
        )

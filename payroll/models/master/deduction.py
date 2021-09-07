from django.db import models
from helpers.models import Model


STATUS_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive')
)

DEDUCTION_COMPONENT_TYPE_CHOICES = (
    ('absent', 'Absent'),
    ('late', 'Late'),
    ('early-out', 'Early Out'),
    ('under-work', 'Under-work'),
    ('other', 'Other')
)

CONDITION_TYPE_CHOICES = (
    ('rule-based', 'Rule Based'),
    ('variable', 'Variable'),
    ('manual-entry', 'Manual Entry')
)

BASIS_TYPE_CHOICES = (
    ('day-basis', 'Day Basis'),
    ('salary-basis', 'On Top of Salary')
)

TIME_UNIT_CHOICES = (
    ('minute', 'Minute'),
    ('hour', 'Hour'),
)

DEDUCT_FROM_CHOICES = [
    ('s', 'Salary'),
    ('l', 'Leave'),
]


class DeductionComponent(Model):
    name = models.CharField(max_length=50)
    short_code = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    deduction_component_type = models.CharField(
        max_length=20,
        choices=DEDUCTION_COMPONENT_TYPE_CHOICES,
        default='absent'
    )

    def __str__(self):
        if self.short_code:
            return "{} - {}".format(self.short_code.upper(), self.name)
        else:
            return "{} - {}".format('', self.name)


class AbsentSetting(Model):
    no_of_absent = models.IntegerField(blank=True, default=0)
    component = models.OneToOneField(DeductionComponent, on_delete=models.CASCADE)
    condition_type = models.CharField(
        max_length=20, blank=True,
        choices=CONDITION_TYPE_CHOICES,
        default='rule-based'
    )
    basis_type = models.CharField(
        max_length=20, blank=True,
        choices=BASIS_TYPE_CHOICES,
        default='day-basis'
    )


class AbsentSettingRBR(Model):  # RBR = Rule Based Relationship
    absent_setting = models.ForeignKey(
        AbsentSetting,
        on_delete=models.CASCADE,
        related_name='rbr_set',
        related_query_name='rbr',
    )
    priority = models.PositiveIntegerField()
    condition = models.TextField(
        default='NULL',
    )
    rule = models.TextField()
    deduct_from = models.CharField(
        max_length=1,
        choices=DEDUCT_FROM_CHOICES,
        default='l',
    )
    salary_component = models.ForeignKey(
        'payroll.Component',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
    )
    leave_component = models.ForeignKey(
        'leave.LeaveMaster',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
    )


class LateSetting(Model):
    component = models.OneToOneField(DeductionComponent, on_delete=models.CASCADE)
    late_grace_time = models.IntegerField(blank=True, default=0)
    late_grace_time_unit = models.CharField(
        max_length=20,
        choices=TIME_UNIT_CHOICES,
        default='minute'
    )
    late_last_time = models.IntegerField(blank=True, default=0)
    late_last_time_unit = models.CharField(
        max_length=20,
        choices=TIME_UNIT_CHOICES,
        default='minute'
    )


class LateSlab(Model):
    component = models.ForeignKey(DeductionComponent, blank=True, on_delete=models.CASCADE)
    time = models.IntegerField(blank=True, null=True)
    unit = models.CharField(
        max_length=20,
        choices=TIME_UNIT_CHOICES,
        default='minute'
    )
    days_to_consider = models.PositiveIntegerField(default=0)
    condition_type = models.CharField(
        max_length=20, blank=True,
        choices=CONDITION_TYPE_CHOICES,
        default='rule-based'
    )
    basis_type = models.CharField(
        max_length=20, blank=True,
        choices=BASIS_TYPE_CHOICES,
        default='day-basis'
    )
    description = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    def __str__(self):
        if self.time:
            return "Slab - {} {}".format(self.time, self.unit)
        else:
            return "Slab - {} {}".format('', self.unit)


class LateSlabRBR(Model):  # RBR = Rule Based Relationship
    late_slab = models.ForeignKey(
        LateSlab,
        on_delete=models.CASCADE,
        related_name='rbr_set',
        related_query_name='rbr',
    )
    priority = models.PositiveIntegerField()
    condition = models.TextField(
        default='NULL',
    )
    rule = models.TextField()
    deduct_from = models.CharField(
        max_length=1,
        choices=DEDUCT_FROM_CHOICES,
        default='l',
    )
    salary_component = models.ForeignKey(
        'payroll.Component',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
    )
    leave_component = models.ForeignKey(
        'leave.LeaveMaster',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
    )


class EarlyOutSetting(Model):
    component = models.OneToOneField(DeductionComponent, on_delete=models.CASCADE)
    early_out_allowed_time = models.IntegerField(blank=True, default=0)
    early_out_allowed_time_unit = models.CharField(
        max_length=20,
        choices=TIME_UNIT_CHOICES,
        default='minute'
    )


class EarlyOutSlab(Model):
    component = models.ForeignKey(DeductionComponent, blank=True, on_delete=models.CASCADE)
    time = models.IntegerField(blank=True, null=True)
    unit = models.CharField(
        max_length=20,
        choices=TIME_UNIT_CHOICES,
        default='minute'
    )
    days_to_consider = models.PositiveIntegerField(default=0)
    condition_type = models.CharField(
        max_length=20, blank=True,
        choices=CONDITION_TYPE_CHOICES,
        default='rule-based'
    )
    basis_type = models.CharField(
        max_length=20, blank=True,
        choices=BASIS_TYPE_CHOICES,
        default='day-basis'
    )
    description = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    def __str__(self):
        if self.time:
            return "Slab - {} {}".format(self.time, self.unit)
        else:
            return "Slab - {} {}".format('', self.unit)


class EarlyOutSlabRBR(Model):  # RBR = Rule Based Relationship
    early_out_slab = models.ForeignKey(
        EarlyOutSlab,
        on_delete=models.CASCADE,
        related_name='rbr_set',
        related_query_name='rbr',
    )
    priority = models.PositiveIntegerField()
    condition = models.TextField(
        default='NULL',
    )
    rule = models.TextField()
    deduct_from = models.CharField(
        max_length=1,
        choices=DEDUCT_FROM_CHOICES,
        default='l',
    )
    salary_component = models.ForeignKey(
        'payroll.Component',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
    )
    leave_component = models.ForeignKey(
        'leave.LeaveMaster',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
    )


class UnderWorkSlab(Model):
    component = models.ForeignKey(DeductionComponent, blank=True, on_delete=models.CASCADE)
    time = models.IntegerField(blank=True, default=0)
    unit = models.CharField(
        max_length=20,
        choices=TIME_UNIT_CHOICES,
        default='minute'
    )
    days_to_consider = models.PositiveIntegerField(default=0)
    condition_type = models.CharField(
        max_length=20, blank=True,
        choices=CONDITION_TYPE_CHOICES,
        default='rule-based'
    )
    basis_type = models.CharField(
        max_length=20, blank=True,
        choices=BASIS_TYPE_CHOICES,
        default='day-basis'
    )
    description = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    def __str__(self):
        if self.time:
            return "Slab - {} {}".format(self.time, self.unit)
        else:
            return "Slab - {} {}".format('', self.unit)


class UnderWorkSlabRBR(Model):  # RBR = Rule Based Relationship
    under_work_slab = models.ForeignKey(
        UnderWorkSlab,
        on_delete=models.CASCADE,
        related_name='rbr_set',
        related_query_name='rbr',
    )
    priority = models.PositiveIntegerField()
    condition = models.TextField(
        default='NULL',
    )
    rule = models.TextField()
    deduct_from = models.CharField(
        max_length=1,
        choices=DEDUCT_FROM_CHOICES,
        default='l',
    )
    salary_component = models.ForeignKey(
        'payroll.Component',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
    )
    leave_component = models.ForeignKey(
        'leave.LeaveMaster',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
    )


class DeductionGroup(Model):
    name = models.CharField(max_length=255)
    short_code = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    absent_component = models.ForeignKey(DeductionComponent, blank=True, null=True,
                                         related_name='group_absent_component', on_delete=models.SET_NULL)
    late_component = models.ForeignKey(DeductionComponent, blank=True, null=True,
                                       related_name='group_late_component', on_delete=models.SET_NULL)
    early_out_component = models.ForeignKey(DeductionComponent, blank=True, null=True,
                                            related_name='group_early_out_component', on_delete=models.SET_NULL)
    under_work_component = models.ForeignKey(DeductionComponent, blank=True, null=True,
                                             related_name='group_under_work_component', on_delete=models.SET_NULL)
    other_component = models.ForeignKey(DeductionComponent, blank=True, null=True,
                                        related_name='group_other_component', on_delete=models.SET_NULL)

    def __str__(self):
        if self.short_code:
            return "{} - {}".format(self.short_code.upper(), self.name)
        else:
            return "{} - {}".format('', self.name)

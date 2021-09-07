from cimbolic.models import Variable
from django.db import models
from helpers.models import Model
from django.utils.text import slugify


STATUS_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive')
)

COMPONENT_TYPE_CHOICES = (
    ('earning', 'Earning'),
    ('deduction', 'Deduction')
)

CONDITION_TYPE_CHOICES = (
    ('rule-based', 'Rule Based'),
    ('variable', 'Variable'),
    ('mapped', 'Mapped with Other Component'),
    ('manual-entry', 'Manual Entry')
)


class Component(Model):
    name = models.CharField(max_length=50)
    short_code = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20, blank=True,
        choices=STATUS_CHOICES,
        default='active'
    )
    component_type = models.CharField(
        max_length=20,
        choices=COMPONENT_TYPE_CHOICES,
        default='earning'
    )
    is_gross = models.BooleanField(default=False, blank=True)
    is_taxable = models.BooleanField(default=False, blank=True)

    def __str__(self):
        if self.short_code:
            return "{} - {}".format(self.short_code.upper(), self.name)
        else:
            return "{} - {}".format('', self.name)


class SalaryGroup(Model):
    component = models.ManyToManyField(Component, through='SalaryGroupComponent')
    name = models.CharField(max_length=50)
    short_code = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    def __str__(self):
        if self.short_code:
            return "{} - {}".format(self.short_code.upper(), self.name)
        else:
            return "{} - {}".format('', self.name)


class SalaryGroupComponent(Model):
    MAPPING_POLICY_CHOICES = (
        ('overtime', 'Overtime'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('under-work', 'Under Work'),
        ('early-out', 'Early Out'),
        ('bonus', 'Bonus'),
    )
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    salary_group = models.ForeignKey(SalaryGroup, on_delete=models.CASCADE)
    variable = models.OneToOneField(
        Variable,
        on_delete=models.SET_NULL,
        related_name='+',
        editable=False,
        null=True,
    )
    condition_type = models.CharField(
        max_length=20, blank=True,
        choices=CONDITION_TYPE_CHOICES,
        default='rule-based'
    )
    mapping_policy = models.CharField(
        max_length=20,
        choices=MAPPING_POLICY_CHOICES,
        default='overtime'
    )
    description = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)
            var = Variable.objects.create(
                name='SGC_{}_{}'.format(slugify(self.salary_group.name).replace('-', '_'), slugify(self.component.name).replace('-', '_')),
                related_data_type=Variable.MODEL_INSTANCE_TYPE,
                related_data_path='payroll.SalaryGroupComponent.{}'.format(self.pk),
            )
            self.variable = var
            self.save()
        else:
            super().save(*args, **kwargs)


class EmployeeVariableSalary(Model):
    salary_structure = models.ForeignKey('employees.SalaryStructure', on_delete=models.CASCADE)
    condition_type = models.CharField(
        max_length=20, blank=True,
        choices=CONDITION_TYPE_CHOICES,
        default='rule-based'
    )
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.BooleanField(default=True)

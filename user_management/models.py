from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
)

from employees.models import EmployeeIdentification
from helpers.models import Model
from setting.models import Branch, Company


class UserManager(BaseUserManager):
    def create_user(self, email, name=None, password=None, is_staff=False,
                    is_management=False, is_superuser=False, is_active=True, user_type=None):
        if not email:
            raise ValueError('Users must have a email address')
        if not password:
            raise ValueError('Users must have a password')

        user_obj = self.model(
            email=self.normalize_email(email),
            name=name,
            management=is_management,
            is_staff=is_staff,
            is_superuser=is_superuser,
            user_type=user_type
        )
        user_obj.active = is_active
        user_obj.set_password(password)
        user_obj.save(using=self._db)

        return user_obj

    def create_staffuser(self, email, name=None, password=None):
        user = self.create_user(
            email,
            name=name,
            password=password,
            is_staff=True
        )
        return user

    def create_superuser(self, email, name=None, password=None):
        user = self.create_user(
            email,
            name=name,
            password=password,
            is_staff=True,
            is_management=True,
            is_superuser=True,
            user_type='system-user'
        )

        return user


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('employee-user', 'Employee User'),
        ('system-user', 'System User')
    )
    DASHBOARD_CHOICES = (
        ('employee', 'Employee'),
        ('management', 'Management'),
        ('admin', 'Admin'),
    )

    name = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES)
    employee = models.OneToOneField(EmployeeIdentification, on_delete=models.CASCADE, blank=True, null=True)
    management = models.BooleanField(default=False, blank=True)
    dashboard = models.CharField(max_length=10, null=True, choices=DASHBOARD_CHOICES)
    groups = models.ManyToManyField(
        Group,
        blank=True,
        through='UserGroup'
    )
    is_staff = models.BooleanField(default=False, blank=True)
    status = models.CharField(max_length=10, blank=True, choices=(
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ), default='active')
    self_panel = models.BooleanField(default=False, blank=True)
    created_at = models.DateTimeField(blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, auto_now=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        if self.user_type == 'employee-user':
            return '%s' % self.employee

        return "%s" % self.name


class UserGroup(Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.group.name


class RoleHierarchy(Model):
    parent_role = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    level = models.PositiveIntegerField()
    role = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.level)


class Workflow(Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=(
        ('undefined', 'Undefined'),
        ('defined', 'Defined')
    ), blank=True, default='undefined')


class WorkflowVariation(Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)


class WorkflowVariationInitiator(Model):
    workflow_variation = models.ForeignKey(WorkflowVariation, on_delete=models.CASCADE)
    initiator = models.ForeignKey(Group, on_delete=models.CASCADE)


class WorkflowVariationLevel(Model):
    workflow_variation = models.ForeignKey(WorkflowVariation, on_delete=models.CASCADE)
    level = models.PositiveIntegerField()


class WorkflowApproval(Model):
    workflow_variation_level = models.ForeignKey(WorkflowVariationLevel, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(Group, on_delete=models.CASCADE)
    next_approval_operator = models.CharField(max_length=3, choices=(
        ('and', 'And'),
        ('or', 'Or')
    ), blank=True, null=True)


class WorkflowNotificationRecipient(Model):
    workflow_variation_level = models.ForeignKey(WorkflowVariationLevel, on_delete=models.CASCADE)
    notification_recipient = models.ManyToManyField(Group, blank=False)


Group.add_to_class('code', models.CharField(max_length=255, blank=True, null=True))
Group.add_to_class('description', models.TextField(blank=True, null=True))
Group.add_to_class('status', models.CharField(max_length=10, blank=True, choices=(
    ('active', 'Active'),
    ('inactive', 'Inactive')
), default='active'))
Group.add_to_class('created_at', models.DateTimeField(auto_now_add=True))
Group.add_to_class('updated_at', models.DateTimeField(auto_now=True))


class Approval(Model):
    TYPE_CHOICES = [
        ('late-entry', 'Late Entry'),
        ('early-out', 'Early Out'),
        ('leave', 'Leave')
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined')
    ]

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    item = models.IntegerField()
    item_type = models.CharField(max_length=10, choices=TYPE_CHOICES, blank=True)
    content_object = GenericForeignKey('content_type', 'item')
    reporting = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE)
    operator = models.CharField(max_length=3, blank=True, null=True)
    level = models.IntegerField(null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=True, default='pending')


class ApprovalNotification(Model):
    content = models.TextField()
    to = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE)

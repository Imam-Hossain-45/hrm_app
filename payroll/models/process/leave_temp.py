from django.db import models
from helpers.models import Model


class LeaveDeduction(Model):
    employee_salary = models.ForeignKey('payroll.EmployeeSalary', on_delete=models.CASCADE)
    avail_leave = models.ForeignKey('leave.LeaveMaster', on_delete=models.SET_NULL, null=True, blank=True)
    credit_seconds = models.IntegerField(default=0)
    notes = models.TextField()
    status = models.BooleanField(default=True)

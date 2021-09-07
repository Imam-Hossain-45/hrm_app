from django.db import models
from helpers.models import Model

STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('with-held', 'With-Held'),
    ('disbursed', 'Disbursed')
)


class EmployeeSalary(Model):
    employee = models.ForeignKey('employees.EmployeeIdentification', blank=True, null=True, on_delete=models.CASCADE)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    disbursed_date = models.DateTimeField(blank=True, null=True)
    net_earning = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_earning = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_deduction = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    def __str__(self):
        return "%s (%s - %s)" % (self.employee.first_name, self.start_date, self.end_date)


class PaySlipComponent(Model):
    employee_salary = models.ForeignKey(EmployeeSalary, on_delete=models.CASCADE)
    condition_type = models.CharField(
        max_length=20, blank=True,
        null=True
    )
    component = models.ForeignKey('payroll.Component', on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.BooleanField(default=True)


class SalaryPaymentMethod(Model):
    employee_salary = models.ForeignKey(EmployeeSalary, on_delete=models.CASCADE, related_name='salary_payment_method')
    payment_mode = models.CharField(max_length=20, choices=[('bank', 'Bank'), ('cash', 'Cash'), ('cheque', 'Cheque'),
                                                            ('fintech', 'Fintech'), ('mixed', 'Mixed')], null=True)


class PaymentDisbursedInfo(Model):
    payment_method = models.ForeignKey(SalaryPaymentMethod, on_delete=models.CASCADE,
                                           related_name='disburse_payment_method')
    payment_mode_for_mixed = models.CharField(max_length=20, choices=[('bank', 'Bank'), ('cash', 'Cash'), ('cheque', 'Cheque'),
                                                            ('fintech', 'Fintech')], null=True, verbose_name='Payment Mode', blank=True)
    employee_bank_name = models.ForeignKey('setting.Bank', on_delete=models.SET_NULL, blank=True, null=True)
    employee_bank_AC_name = models.CharField(max_length=255, blank=True, null=True,
                                             verbose_name='Employee Bank A/C Name')
    bank_branch_code = models.CharField(max_length=255, blank=True, null=True)
    bank_AC_no = models.IntegerField(blank=True, null=True, verbose_name='Bank A/C No')
    routing_number = models.CharField(max_length=255, blank=True, null=True)
    cheque_number = models.IntegerField(null=True, blank=True)
    fintech_service = models.CharField(max_length=20,
                                       choices=[('bkash', 'bkash'), ('rocket', 'Rocket'), ('upay', 'Upay'),
                                                ('nagad', 'Nagad'), ('mcash', 'mCash'), ('dmoney', 'Dmoney'),
                                                ('other', 'Other')], null=True, verbose_name="Select Service", blank=True)
    mobile_number = models.CharField(max_length=255, blank=True, null=True)
    disbursed_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

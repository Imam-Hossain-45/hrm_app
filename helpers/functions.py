from decimal import Decimal
from typing import Optional, Union

from django.db.models import F, Max

from cimbolic.models import Variable

from employees.models import EmployeeIdentification, JobInformation
from leave.models import LeaveAvail, LeaveRemaining
from payroll.models import EmployeeSalary, LeaveDeduction
from setting.models import OrganizationalStructure


def parse_single_formula(condition: str, rule: str) -> Optional[Union[int, Decimal]]:
    """Cimbolically parse a single formula, ignoring priority."""
    max_id = Variable.objects.aggregate(max_id=Max('id')).get('max_id', 0)
    unique_var_name = 'CIMPLUXXX_TMP_{}'.format(max_id)
    var = Variable.objects.create(name=unique_var_name)
    if condition.upper() == 'NULL':
        condition = 'NULL'
    else:
        var.add_formula('NULL', 'CIMPLUXXX', 2)
    var.add_formula(condition, rule, 1)
    try:
        value = var.to_value()
    except Exception:
        value = None
    var.delete()
    return value


def execute_leave_deductions(employee_salary: EmployeeSalary) -> None:
    """Execute stored deductions from leave."""
    employee = employee_salary.employee
    leave_deductions_qs = LeaveDeduction.objects.filter(employee_salary=employee_salary)
    if leave_deductions_qs.exists():
        for leave_deduction in leave_deductions_qs:
            LeaveAvail.objects.create(
                employee=employee,
                avail_leave=leave_deduction.avail_leave,
                credit_seconds=leave_deduction.credit_seconds,
                notes=leave_deduction.notes,
            )
            leave_remaining = LeaveRemaining.objects.get(employee=employee, leave=leave_deduction.avail_leave,
                                                         status=True)
            leave_remaining.remaining_in_seconds = F('remaining_in_seconds') - leave_deduction.credit_seconds
            leave_remaining.save(update_fields=['remaining_in_seconds'])
        leave_deductions_qs.delete()


def get_organizational_structure():
    structure_items_qs = OrganizationalStructure.objects.all()
    items_list = []

    for structure_item in structure_items_qs:
        items_list.append(structure_item.item)

    return items_list


def get_employee_query_info(employee):
    results = EmployeeIdentification.objects.filter(id=employee)
    data = dict()

    for result in results:
        data['id'] = result.id
        data['name'] = result.get_title_display() + ' ' + result.first_name + ' ' + result.middle_name + ' ' + result.last_name
        data['employee_id'] = result.employee_id or ''
        try:
            job = JobInformation.objects.filter(employee=result).latest('updated_at')
            designation = job.designation.name
        except:
            designation = ' '

        data['designation'] = designation

    return data



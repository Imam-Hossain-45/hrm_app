from typing import List, Optional, Tuple, Union
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from helpers import daily_record
from helpers.mixins import PermissionMixin
from django.contrib import messages
from payroll.forms import SearchForm
from django.shortcuts import render
from employees.models import EmployeeIdentification, Attendance, SalaryStructure, LeaveManage, Payment
from payroll.models import (EmployeeSalary, SalaryGroupComponent, EmployeeVariableSalary, AbsentSetting,
                            LateSetting, LateSlab, EarlyOutSetting, EarlyOutSlab, UnderWorkSlab, PaySlipComponent,
                            SalaryPaymentMethod, PaymentDisbursedInfo, LeaveDeduction)
from datetime import datetime, timedelta
from attendance.models import WorkDaySchedule, DailyRecord, ScheduleRecord
from decimal import Decimal
from helpers.functions import parse_single_formula, get_organizational_structure

SettingType = Union[AbsentSetting, LateSlab, EarlyOutSlab, UnderWorkSlab]

# List of row ID's (DO NOT ACCESS UNLESS YOU KNOW WHAT YOU ARE DOING)
FORCEFULLY_CHANGED_COMPONENTS: List[int] = []


def evaluate_RBR(setting: SettingType, employee: EmployeeIdentification, freq: int) -> List[Optional[Tuple]]:
    """Evaluate a Rule-Based Relationship set.

    If no conditions are met: [] is returned.
    The function returns as soons as:
        - all the rule-based sets are evaluated
        - a salary deduction is satisfied (last element is a salary deduction)
        - an error is encountered (last element is None)
    """
    values = []
    rbr_set = setting.rbr_set.order_by('priority')
    for rbr in rbr_set:
        parsed_value = parse_single_formula(rbr.condition, rbr.rule)
        if parsed_value is None:
            values.append(None)
            break
        if rbr.deduct_from == 's':  # salary
            values.append(('salary', rbr.salary_component, parsed_value, freq))
            break
        if rbr.deduct_from == 'l':  # leave
            if not employee.leaveremaining_set.filter(leave=rbr.leave_component).exists():
                continue
            leave_remaining = employee.leaveremaining_set.filter(leave=rbr.leave_component).first()
            leave_remaining_second = leave_remaining.remaining_in_seconds
            time_unit = rbr.leave_component.time_unit_basis
            avail_seconds = 0
            if time_unit == 'day':
                while (leave_remaining_second - (parsed_value * 24 * 3600) < 0) and (freq > 0):
                    avail_seconds += (parsed_value * 24 * 3600)
                    leave_remaining_second -= (parsed_value * 24 * 3600)
                    freq -= 1
            elif time_unit == 'hour':
                while (leave_remaining_second - (parsed_value * 3600) < 0) and (freq > 0):
                    avail_seconds += (parsed_value * 3600)
                    leave_remaining_second -= (parsed_value * 3600)
                    freq -= 1
            elif time_unit == 'week':
                while (leave_remaining_second - (parsed_value * 7 * 24 * 3600) < 0) and (freq > 0):
                    avail_seconds += (parsed_value * 7 * 24 * 3600)
                    leave_remaining_second -= (parsed_value * 7 * 24 * 3600)
                    freq -= 1
            else:
                while (leave_remaining_second - (parsed_value * 30 * 24 * 3600) < 0) and (freq > 0):
                    avail_seconds += (parsed_value * 30 * 24 * 3600)
                    leave_remaining_second -= (parsed_value * 30 * 24 * 3600)
                    freq -= 1
            values.append(('leave', rbr.leave_component, avail_seconds, freq))
    return values


class SalaryProcessGenerate(LoginRequiredMixin, PermissionMixin, ListView):
    """
        Process payroll for the selected employees
    """

    model = EmployeeSalary
    template_name = "payroll/process/salary_process/generate.html"
    permission_required = 'add_employeesalary'

    def get_context_data(self, **kwargs):
        FORCEFULLY_CHANGED_COMPONENTS.clear()
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['form'] = SearchForm()
        return context

    def check_process_salary(self, employee, st_date, en_date):
        start_date = datetime.strptime(st_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(en_date, '%Y-%m-%d').date()

        if not EmployeeSalary.objects.filter(employee=employee, status='disbursed').exists():
            if self.month_validation(start_date, end_date):
                # process the salary for the given range
                return self.process_salary(employee, start_date, end_date)
            else:
                return None, 'Invalid date range for the employee to process salary'
        else:
            # check the last disbursed end date and check if the new process start date is +1. if not then don't allow
            # the process. Otherwise process the salary for the given range if valid

            if self.valid_date_range(employee, start_date, end_date):
                return self.process_salary(employee, start_date, end_date)
            else:
                # invalid date range to process salary of the employee
                return None, 'Invalid date range for the employee to process salary'

    def valid_date_range(self, employee, start_date, end_date):
        last_disbursed_salary = EmployeeSalary.objects.filter(employee=employee, status='disbursed').last()
        last_disbursed_salary_end_date = last_disbursed_salary.end_date

        if start_date == (last_disbursed_salary_end_date + timedelta(days=1)):
            if self.month_validation(start_date, end_date):
                return True
        return False

    def month_validation(self, start_date, end_date):
        is_first_day_of_month = True if start_date.day == 1 else False
        is_last_day_of_month = True if end_date.month == start_date.month and (
            end_date + timedelta(days=1)).month != start_date.month and datetime.now().date() >= end_date else False
        if is_first_day_of_month and is_last_day_of_month:
            return True
        return False

    def process_salary(self, employee, start_date, end_date):
        # valid date range to process salary for the employee

        # get info of employee schedule. e.g.,
        # 1. what type of schedule does this employee belong to?
        # 2. how many hours does he need to work per day/week/month etc.?

        if Attendance.objects.filter(employee=employee).exists():
            employee_schedule_object = Attendance.objects.get(employee=employee)
            employee_schedule = employee_schedule_object.schedule_type

            if employee_schedule is None:
                return None, 'No employee schedule is defined in employee master'

            employee_schedule_type = employee_schedule.schedule_type
            if SalaryStructure.objects.filter(employee=employee).exists():
                employee_salary_structure = self.get_salary_structure(employee, start_date, end_date)
                # if any employee_salary_structure object matches the processing date query go process otherwise not
                if employee_salary_structure:
                    # get schedule information to process
                    salary_group = employee_salary_structure.salary_group
                    # get all the components of this group then process
                    salary_group_components = SalaryGroupComponent.objects.filter(salary_group=salary_group)
                    total_earning = 0
                    total_deduction = 0
                    salary_context = {}  # all the salary components with their corresponding values
                    leave_deduction_list = []
                    roster_type = None

                    """Save data in ScheduleRecord and DailyRecord"""
                    daily_record_data = {
                        'employee': employee.id,
                        'date': end_date
                    }

                    daily_record.set_daily_record(daily_record_data)

                    if employee_schedule_type == 'roster':
                        roster_type = employee_schedule.roster_type
                    if (employee_schedule_type in ['regular-fixed-time', 'fixed-day']) or \
                            (roster_type in ['fixed-roster', 'variable-roster']):
                        for salary_group_component in salary_group_components:
                            if salary_group_component.condition_type == 'variable':
                                if not EmployeeVariableSalary.objects.filter(salary_structure=employee_salary_structure,
                                                                             component=salary_group_component.component
                                                                             ).exists():
                                    message = 'Improper salary settings for: ' + str(salary_group_component.component) + \
                                              '. Check salary settings of the employee in the employee master.'
                                    return None, message
                                employee_salary_object = \
                                    EmployeeVariableSalary.objects.get(salary_structure=employee_salary_structure,
                                                                       component=salary_group_component.component)
                                salary_group_component.variable.formulae.all().delete()
                                salary_group_component.variable.add_formula('NULL', '{}'.format(employee_salary_object.value), 1)
                                FORCEFULLY_CHANGED_COMPONENTS.append(salary_group_component.id)

                        for salary_group_component in salary_group_components:
                            if not EmployeeVariableSalary.objects.filter(salary_structure=employee_salary_structure,
                                                                         component=salary_group_component.component
                                                                         ).exists():
                                message = 'Improper salary settings for: ' + str(salary_group_component.component) + \
                                          '. Check salary settings of the employee in the employee master.'
                                return None, message
                            employee_salary_object = \
                                EmployeeVariableSalary.objects.get(salary_structure=employee_salary_structure,
                                                                   component=salary_group_component.component)
                            component_value = 0
                            if salary_group_component.condition_type == 'rule-based':
                                try:
                                    component_value = salary_group_component.variable.to_value()
                                except Exception as e:
                                    message = 'Error: occurred while parsing '+str(salary_group_component.component)
                                    return None, message
                            elif salary_group_component.condition_type == 'variable':
                                component_value = employee_salary_object.value
                            elif salary_group_component.condition_type == 'mapped':
                                mapping_policy = salary_group_component.mapping_policy
                                if mapping_policy == 'overtime':
                                    overtime_value, message = self.get_overtime_value(employee, start_date, end_date)
                                    if overtime_value is None:
                                        return None, message
                                    component_value = overtime_value
                                elif mapping_policy == 'bonus':
                                    component_value = 0
                                elif mapping_policy == 'absent':
                                    total_absents, message = \
                                        self.get_employee_total_absent(employee, start_date, end_date)
                                    if total_absents is None:
                                        return None, message
                                    component_value, leave_deductions = self.get_absent_value(employee, total_absents)
                                    if component_value is None:
                                        return None, leave_deductions
                                    leave_deduction_per_mapping = (leave_deductions, 'deducted for absent')
                                    leave_deduction_list.append(leave_deduction_per_mapping)
                                elif mapping_policy == 'late':
                                    component_value, leave_deductions = self.get_late_value(employee, start_date, end_date)
                                    if component_value is None:
                                        return None, leave_deductions
                                    leave_deduction_per_mapping = (leave_deductions, 'deducted for late')
                                    leave_deduction_list.append(leave_deduction_per_mapping)
                                elif mapping_policy == 'under-work':
                                    component_value, leave_deductions = \
                                        self.get_under_work_value(employee, start_date, end_date)
                                    if component_value is None:
                                        return None, leave_deductions
                                    leave_deduction_per_mapping = (leave_deductions, 'deducted for under-work')
                                    leave_deduction_list.append(leave_deduction_per_mapping)
                                elif mapping_policy == 'early-out':
                                    component_value, leave_deductions = self.get_early_out_value(employee, start_date, end_date)
                                    if component_value is None:
                                        return None, leave_deductions
                                    leave_deduction_per_mapping = (leave_deductions, 'deducted for early-out')
                                    leave_deduction_list.append(leave_deduction_per_mapping)
                            elif salary_group_component.condition_type == 'manual-entry':
                                component_value = 0

                            if not salary_group_component.component.is_gross:
                                if salary_group_component.component.component_type == 'earning':
                                    total_earning = Decimal(total_earning) + Decimal(component_value)
                                elif salary_group_component.component.component_type == 'deduction':
                                    total_deduction = Decimal(total_deduction) + Decimal(component_value)
                            salary_context[salary_group_component] = component_value

                        net_earning = total_earning - total_deduction
                        # print('total salary -> ', net_earning)
                        # print('Total Earning -> ', total_earning)
                        # print('Total Deduction -> ', total_deduction)
                        # print('salary_context -> ', salary_context)

                        # [MODEL-NAME._meta.get_field('FIELD-NAME').default] -> this gives the default value set for
                        # the model field
                        total_working_days_of_month = \
                            WorkDaySchedule._meta.get_field('total_working_day_of_month').default

                        # # print each day salary
                        # salary_per_day = Decimal(net_earning)/Decimal(total_working_days_of_month)
                        # print('Per day Salary -> ', salary_per_day)
                        #
                        # insert calculated salary values to database
                        # 1. insert the total salary information to EmployeeSalary table
                        # 2. insert each components calculated values with the recently created row in EmployeeSalary
                        #    in the PaySlipComponent table
                        try:
                            newly_created_employee_salary_object, created = EmployeeSalary.objects.update_or_create(
                                status__in=['draft', 'confirmed', 'with-held'], employee=employee,
                                defaults={
                                    'net_earning': round(net_earning, 2),
                                    'total_earning': round(total_earning, 2),
                                    'total_deduction': round(total_deduction, 2),
                                    'start_date': start_date,
                                    'end_date': end_date,
                                    'status': 'draft'
                                }
                            )
                        except:
                            return None, 'Check database for multiple non-disbursed rows'

                        # all the salary components with their corresponding per day values
                        salary_per_day_context = {}
                        for data, value in salary_context.items():
                            # # print each salary component value for the month
                            # print(data.component, '->', value)
                            employee_variable_salary_object = EmployeeVariableSalary.objects.get(
                                component=data.component, salary_structure=employee_salary_structure
                            )
                            PaySlipComponent.objects.update_or_create(
                                employee_salary=newly_created_employee_salary_object,
                                condition_type=employee_variable_salary_object.condition_type,
                                component=employee_variable_salary_object.component,
                                defaults={
                                    'value': value,
                                }
                            )
                            # calculate each day salary for the employee and store it in the context
                            if data.condition_type in ['variable', 'rule-based']:
                                salary_per_day_context[data] = Decimal(value)/Decimal(total_working_days_of_month)

                        # # print per-day salary of the employee
                        # for data, value in salary_per_day_context.items():
                        #     print(data.component, '->', value)

                        if Payment.objects.filter(employee=employee).exists():
                            employee_payment_method = Payment.objects.get(employee=employee)
                            salary_payment_method, created = SalaryPaymentMethod.objects.update_or_create(
                                employee_salary=newly_created_employee_salary_object,
                                defaults={
                                    'payment_mode': employee_payment_method.payment_mode,
                                }
                            )
                            PaymentDisbursedInfo.objects.update_or_create(
                                payment_method=salary_payment_method,
                                defaults={
                                    'employee_bank_name': employee_payment_method.employee_bank_name,
                                    'employee_bank_AC_name': employee_payment_method.employee_bank_AC_name,
                                    'bank_branch_code': employee_payment_method.bank_branch_code,
                                    'bank_AC_no': employee_payment_method.bank_AC_no,
                                    'routing_number': employee_payment_method.routing_number,
                                }
                            )
                        else:
                            salary_payment_method = SalaryPaymentMethod.objects.create(
                                employee_salary=newly_created_employee_salary_object, payment_mode='cash'
                            )
                            PaymentDisbursedInfo.objects.create(payment_method=salary_payment_method)

                        # delete all the leaves to deduct, so that we can add new objects.
                        LeaveDeduction.objects.filter(employee_salary=newly_created_employee_salary_object).delete()
                        for ld in leave_deduction_list:
                            if ld[0]:
                                LeaveDeduction.objects.create(
                                    employee_salary=newly_created_employee_salary_object,
                                    avail_leave=ld[0][0][1],
                                    credit_seconds=ld[0][0][2],
                                    notes=ld[1],
                                )
                        return newly_created_employee_salary_object, 'successful processing'
                    return None, 'Schedule not supported by BeeHive right now'
                return None, 'Employee Salary Structure for the processing time-frame is not defined, ' \
                             'Select a Salary Structure first for the employee in the employee-master ' \
                             'for the time-frame to process salary'
            return None, 'Employee does not have any salary structure defined, ' \
                         'Select a Salary Structure first for the employee in the employee-master to process salary'
        return None, 'Employee Attendance info does not exist, ' \
                     'Create Attendance info first for the employee in the employee-master to process salary'

    def get_salary_structure(self, employee, start_date, end_date):
        employee_salary_structures = SalaryStructure.objects.filter(employee=employee)
        for salary_structure in employee_salary_structures:
            if ((start_date >= salary_structure.from_date and not salary_structure.to_date) or
                    (start_date >= salary_structure.from_date and end_date <= salary_structure.to_date)):
                return salary_structure
        return None

    def get_absent_value(self, employee, total_absents):
        if not LeaveManage.objects.filter(employee=employee).exists():
            return 0, []
        employee_deduction_object = LeaveManage.objects.get(employee=employee)
        deduction_group = employee_deduction_object.deduction_group
        if deduction_group is None:
            return 0, []
        absent_component = deduction_group.absent_component
        if (not absent_component or absent_component.deduction_component_type != 'absent' or
                not AbsentSetting.objects.filter(component=absent_component).exists()):
            return 0, []

        absent_setting_object = AbsentSetting.objects.get(component=absent_component)
        if absent_setting_object.no_of_absent == 0:
            return 0, []

        absent_frequency_by_policy = int(total_absents/absent_setting_object.no_of_absent)
        condition_type = absent_setting_object.condition_type
        basis_type = absent_setting_object.basis_type

        if condition_type == 'rule-based':
            rbr_values = evaluate_RBR(absent_setting_object, employee, absent_frequency_by_policy)
            if None in rbr_values:
                return None, 'Error: occurred while parsing absent mapping component'
            if not rbr_values:
                return 0, []
            leave_deduction_list = []
            salary_deduction_tuple = None
            for rbrval in rbr_values:
                if rbrval[0] == 'leave':
                    leave_deduction_list.append(rbrval)
                else:
                    salary_deduction_tuple = (rbrval[2], rbrval[3])
            if not salary_deduction_tuple:
                return 0, leave_deduction_list
            value, frequency = salary_deduction_tuple
            if basis_type == 'day-basis':
                return value * frequency, leave_deduction_list
            elif basis_type == 'salary-basis':
                return value, leave_deduction_list
        return None, 'Invalid Condition Type'

    def get_employee_total_absent(self, employee, start_date, end_date):
        # get info of each date in the process range
        total_absents = 0
        processing_date = start_date
        while processing_date <= end_date:
            if not ScheduleRecord.objects.filter(employee=employee, date=processing_date).exists():
                return None, 'Error: Attendance Record does not exist for the date: ' + str(processing_date)
            record = ScheduleRecord.objects.get(employee=employee, date=processing_date)
            if record.is_working_day and not record.dailyrecord.is_present and not record.dailyrecord.is_leave_paid:
                total_absents += 1
            processing_date = processing_date + timedelta(days=1)  # date increment
        # loop ends

        return total_absents, None

    def get_overtime_value(self, employee, start_date, end_date):
        employee_overtime_object = LeaveManage.objects.get(employee=employee)
        message = 'Valid'
        if not employee_overtime_object:
            return 0, message
        if not employee_overtime_object.overtime:
            return 0, message
        overtime_object = employee_overtime_object.overtime_group
        if overtime_object is None:
            return 0, message

        # Initial values to calculate
        total_overtime_days = 0
        total_post_overtime = 0
        total_pre_overtime = 0
        overtime_type = overtime_object.segment

        default_calculation_unit = overtime_object.default_calculation_unit

        if overtime_type in ['post', 'both']:
            minimum_working_duration_post = overtime_object.minimum_working_duration_post
            minimum_working_duration_unit_post = overtime_object.minimum_working_duration_unit_post
            buffer_duration_post = overtime_object.buffer_duration_post
            buffer_duration_unit_post = overtime_object.buffer_duration_unit_post
            try:
                max_duration_restriction_post = overtime_object.duration_restrictions.filter(ot_segment='post').first()
            except:
                message = 'Max duration for post-overtime is not defined'
                return 0, message

            buffer_duration_post = buffer_duration_post * 60 if buffer_duration_unit_post == 'm' else \
                buffer_duration_post * 3600

            minimum_working_duration_post = \
                minimum_working_duration_post * 60 if minimum_working_duration_unit_post == 'm' else \
                minimum_working_duration_post * 3600

            tolerance_time_post = overtime_object.tolerance_time_post

            if default_calculation_unit == 'h':
                tolerance_time_post = tolerance_time_post * 60

            maximum_duration_post = 0
            if max_duration_restriction_post is not None:
                maximum_duration_post = max_duration_restriction_post.maximum_duration
                maximum_duration_post_unit = max_duration_restriction_post.maximum_duration_unit
                if maximum_duration_post_unit == 'h':
                    maximum_duration_post = maximum_duration_post * 3600
                elif maximum_duration_post_unit == 'm':
                    maximum_duration_post = maximum_duration_post * 60

        else:
            minimum_working_duration_post = 0
            buffer_duration_post = 0
            tolerance_time_post = 0
            maximum_duration_post = 0
            max_duration_restriction_post = None

        if overtime_type in ['pre', 'both']:
            minimum_working_duration_pre = overtime_object.minimum_working_duration_pre
            minimum_working_duration_unit_pre = overtime_object.minimum_working_duration_unit_pre
            buffer_duration_pre = overtime_object.buffer_duration_pre
            buffer_duration_unit_pre = overtime_object.buffer_duration_unit_pre
            try:
                max_duration_restriction_pre = overtime_object.duration_restrictions.filter(ot_segment='pre').first()
            except:
                message = 'Max duration for pre-overtime is not defined'
                return 0, message

            buffer_duration_pre = buffer_duration_pre * 60 if buffer_duration_unit_pre == 'm' else \
                buffer_duration_pre * 3600

            minimum_working_duration_pre = \
                minimum_working_duration_pre * 60 if minimum_working_duration_unit_pre == 'm' else \
                minimum_working_duration_pre * 3600

            tolerance_time_pre = overtime_object.tolerance_time_pre

            if default_calculation_unit == 'h':
                tolerance_time_pre = tolerance_time_pre * 60

            maximum_duration_pre = 0
            if max_duration_restriction_pre is not None:
                maximum_duration_pre = max_duration_restriction_pre.maximum_duration
                maximum_duration_pre_unit = max_duration_restriction_pre.maximum_duration_unit
                if maximum_duration_pre_unit == 'h':
                    maximum_duration_pre = maximum_duration_pre * 3600
                elif maximum_duration_pre_unit == 'm':
                    maximum_duration_pre = maximum_duration_pre * 60

        else:
            minimum_working_duration_pre = 0
            buffer_duration_pre = 0
            tolerance_time_pre = 0
            maximum_duration_pre = 0
            max_duration_restriction_pre = None

        processing_date = start_date
        while processing_date <= end_date:
            if not ScheduleRecord.objects.filter(employee=employee, date=processing_date).exists():
                return None, 'Error: Attendance Record does not exist for the date: ' + str(processing_date)

            record = ScheduleRecord.objects.get(employee=employee, date=processing_date)
            if record.dailyrecord.is_overtime:
                if not (record.is_working_day and not record.dailyrecord.is_present and not record.dailyrecord.is_leave_paid):
                    # employee is present for the day
                    if overtime_type in ['post', 'both']:
                        daily_post_overtime_seconds = record.dailyrecord.daily_post_overtime_seconds
                        calculable_daily_post_overtime_seconds = daily_post_overtime_seconds - buffer_duration_post

                        if calculable_daily_post_overtime_seconds >= minimum_working_duration_post:
                            # post-overtime exist for the day
                            total_overtime_days += 1
                            whole_number_post_overtime = \
                                int(calculable_daily_post_overtime_seconds/3600) if \
                                default_calculation_unit == 'h' else int(calculable_daily_post_overtime_seconds/60)
                            rem_number_post_overtime = calculable_daily_post_overtime_seconds % 3600 if \
                                default_calculation_unit == 'h' else calculable_daily_post_overtime_seconds % 60

                            if rem_number_post_overtime >= tolerance_time_post:
                                whole_number_post_overtime += 1

                            # convert whole number hour/minute to seconds
                            whole_number_post_overtime = \
                                whole_number_post_overtime * 3600 if default_calculation_unit == 'h' else \
                                whole_number_post_overtime * 60
                            if max_duration_restriction_post is not None:
                                if whole_number_post_overtime > maximum_duration_post > 0:
                                    whole_number_post_overtime = maximum_duration_post

                            whole_number_calculated_post_overtime = \
                                int(whole_number_post_overtime / 3600) if \
                                default_calculation_unit == 'h' else int(whole_number_post_overtime / 60)

                            total_post_overtime += whole_number_calculated_post_overtime
                            # use minute/hour format to parse and calculate
                            record.dailyrecord.countable_post_overtime = whole_number_post_overtime
                            # save seconds format in the database
                            record.dailyrecord.save()

                    if overtime_type in ['pre', 'both']:
                        daily_pre_overtime_seconds = record.dailyrecord.daily_pre_overtime_seconds
                        calculable_daily_pre_overtime_seconds = daily_pre_overtime_seconds - buffer_duration_pre

                        if calculable_daily_pre_overtime_seconds >= minimum_working_duration_pre:
                            # pre-overtime exist for the day
                            total_overtime_days += 1
                            whole_number_pre_overtime = \
                                int(calculable_daily_pre_overtime_seconds / 3600) if \
                                default_calculation_unit == 'h' else int(calculable_daily_pre_overtime_seconds / 60)
                            rem_number_pre_overtime = calculable_daily_pre_overtime_seconds % 3600 if \
                                default_calculation_unit == 'h' else calculable_daily_pre_overtime_seconds % 60

                            if rem_number_pre_overtime >= tolerance_time_pre:
                                whole_number_pre_overtime += 1

                            # convert whole number hour/minute to seconds
                            whole_number_pre_overtime = \
                                whole_number_pre_overtime * 3600 if default_calculation_unit == 'h' else \
                                whole_number_pre_overtime * 60
                            if max_duration_restriction_pre is not None:
                                if whole_number_pre_overtime > maximum_duration_pre > 0:
                                    whole_number_pre_overtime = maximum_duration_pre

                            whole_number_calculated_pre_overtime = \
                                int(whole_number_pre_overtime / 3600) if \
                                default_calculation_unit == 'h' else int(whole_number_pre_overtime / 60)

                            total_pre_overtime += whole_number_calculated_pre_overtime
                            # use minute/hour format to parse and calculate
                            record.dailyrecord.countable_pre_overtime = whole_number_pre_overtime
                            # save seconds format in the database
                            record.dailyrecord.save()

            processing_date = processing_date + timedelta(days=1)  # date increment
        # loop ends

        total_overtime = total_post_overtime + total_pre_overtime

        if total_overtime == 0:
            return 0, message

        calc_method = overtime_object.active_wage_calculation_model
        if calc_method.method == 'fixed-rate':
            if calc_method.basis == 'm':
                ot_mins = total_overtime // 60
                return ot_mins * calc_method.amount, message
            if calc_method.basis == 'h':
                ot_hours = total_overtime // 3600
                return ot_hours * calc_method.amount, message
            if calc_method.basis == 'd':
                return total_overtime_days * calc_method.amount, message
            if calc_method.basis == 's':
                return calc_method.amount, message
        if calc_method.method == 'rule-based':
            amount = calc_method.variable.to_value()
            if calc_method.basis == 'm':
                ot_mins = total_overtime // 60
                return ot_mins * amount, message
            if calc_method.basis == 'h':
                ot_hours = total_overtime // 3600
                return ot_hours * amount, message
            if calc_method.basis == 'd':
                return total_overtime_days * amount, message
            if calc_method.basis == 's':
                return amount, message
        return 0, message

    def get_late_value(self, employee, start_date, end_date):
        employee_deduction_object = LeaveManage.objects.get(employee=employee)
        deduction_group = employee_deduction_object.deduction_group
        if deduction_group is None:
            return 0, []
        late_component = deduction_group.late_component
        if (not late_component or late_component.deduction_component_type != 'late' or
                not LateSetting.objects.filter(component=late_component).exists()):
            return 0, []

        late_slab_objects = LateSlab.objects.filter(component=late_component)
        if not late_slab_objects.exists():
            return 0, []
        late_slab_context = {}

        for late_slab_object in late_slab_objects:
            late_slab_context[late_slab_object] = \
                late_slab_object.time if late_slab_object.unit == 'minute' else late_slab_object.time*60

        sorted_late_slab_context = sorted(late_slab_context.items(), key=lambda x: x[1])
        sorted_late_slab_appearance_counter_context = {}
        for data, slab_value in sorted_late_slab_context:
            sorted_late_slab_appearance_counter_context[data] = 0
        total_late = 0
        processing_date = start_date
        while processing_date <= end_date:
            if not ScheduleRecord.objects.filter(employee=employee, date=processing_date).exists():
                return None, 'Error: Attendance Record does not exist for the date: ' + str(processing_date)
            record = ScheduleRecord.objects.get(employee=employee, date=processing_date)
            if not record.is_weekend or record.is_holiday:
                if not (record.is_working_day and not record.dailyrecord.is_present and not record.dailyrecord.is_leave_paid):
                    # employee is present for the day
                    if record.dailyrecord.late:
                        late_value = int(record.dailyrecord.late_value / 60)
                        total_late += 1
                        got_slab = False
                        for data, slab_value in sorted_late_slab_context:
                            if late_value <= slab_value:
                                sorted_late_slab_appearance_counter_context[data] += 1
                                got_slab = True
                                break

                        if not got_slab:
                            sorted_late_slab_appearance_counter_context[sorted_late_slab_context[-1][0]] += 1

            processing_date = processing_date + timedelta(days=1)  # date increment
        # loop ends

        dec_sorted_late_slab_appearance_counter_context = \
            sorted(sorted_late_slab_appearance_counter_context.items(),
                   key=lambda x: x[0].time if x[0].unit == 'minute' else x[0].time*60, reverse=True)

        deduction_list = []
        total_deducted_value = 0

        if total_late > 0:
            carry_over = 0
            for slab, late_appearance in dec_sorted_late_slab_appearance_counter_context:
                total_late_appearance = late_appearance + carry_over
                if slab.days_to_consider > 0:
                    late_to_count = int(total_late_appearance / slab.days_to_consider)
                    if late_to_count != 0:
                        # get deducted value
                        condition_type = slab.condition_type
                        basis_type = slab.basis_type

                        if condition_type == 'rule-based':
                            rbr_values = evaluate_RBR(slab, employee, late_to_count)
                            if None in rbr_values:
                                return None, 'Error: occurred while parsing late mapping component'
                            if rbr_values:
                                leave_deduction_list = []
                                salary_deduction_tuple = None
                                for rbrval in rbr_values:
                                    if rbrval[0] == 'leave':
                                        leave_deduction_list.append(rbrval)
                                    else:
                                        salary_deduction_tuple = (rbrval[2], rbrval[3])
                                if salary_deduction_tuple: # no salary deduction found but a list of leave deduction maybe found
                                    value, total_late_appearance = salary_deduction_tuple
                                    if basis_type == 'day-basis':
                                        total_deducted_value += (value * total_late_appearance)
                                    elif basis_type == 'salary-basis':
                                        total_deducted_value += value

                                deduction_list += leave_deduction_list
                    carry_over = total_late_appearance % slab.days_to_consider
                else:
                    carry_over = total_late_appearance
        return total_deducted_value, deduction_list

    def get_early_out_value(self, employee, start_date, end_date):
        employee_deduction_object = LeaveManage.objects.get(employee=employee)
        deduction_group = employee_deduction_object.deduction_group
        if deduction_group is None:
            return 0, []
        early_out_component = deduction_group.early_out_component
        if (not early_out_component or early_out_component.deduction_component_type != 'early-out' or
                not EarlyOutSetting.objects.filter(component=early_out_component).exists()):
            return 0, []

        early_out_slab_objects = EarlyOutSlab.objects.filter(component=early_out_component)
        if not early_out_slab_objects.exists():
            return 0, []
        early_out_slab_context = {}

        for early_out_slab_object in early_out_slab_objects:
            early_out_slab_context[early_out_slab_object] = \
                early_out_slab_object.time if early_out_slab_object.unit == 'minute' else early_out_slab_object.time * 60

        sorted_early_out_slab_context = sorted(early_out_slab_context.items(), key=lambda x: x[1])
        sorted_early_out_slab_appearance_counter_context = {}
        for data, slab_value in sorted_early_out_slab_context:
            sorted_early_out_slab_appearance_counter_context[data] = 0
        total_early_out = 0

        processing_date = start_date
        while processing_date <= end_date:
            if not ScheduleRecord.objects.filter(employee=employee, date=processing_date).exists():
                return None, 'Error: Attendance Record does not exist for the date: ' + str(processing_date)
            record = ScheduleRecord.objects.get(employee=employee, date=processing_date)
            if not record.is_weekend or record.is_holiday:
                if not (record.is_working_day and not record.dailyrecord.is_present and not record.dailyrecord.is_leave_paid):
                    # employee is present for the day
                    if record.dailyrecord.early:
                        early_out_value = int(record.dailyrecord.early_out_value / 60)
                        total_early_out += 1
                        got_slab = False
                        for data, slab_value in sorted_early_out_slab_context:
                            if early_out_value <= slab_value:
                                sorted_early_out_slab_appearance_counter_context[data] += 1
                                got_slab = True
                                break

                        if not got_slab:
                            sorted_early_out_slab_appearance_counter_context[sorted_early_out_slab_context[-1][0]] += 1

            processing_date = processing_date + timedelta(days=1)  # date increment
        # loop ends

        dec_sorted_early_out_slab_appearance_counter_context = \
            sorted(sorted_early_out_slab_appearance_counter_context.items(),
                   key=lambda x: x[0].time if x[0].unit == 'minute' else x[0].time * 60, reverse=True)

        deduction_list = []
        total_deducted_value = 0
        if total_early_out > 0:
            carry_over = 0
            for slab, early_out_appearance in dec_sorted_early_out_slab_appearance_counter_context:
                total_early_out_appearance = early_out_appearance + carry_over

                if slab.days_to_consider > 0:
                    early_out_to_count = int(total_early_out_appearance / slab.days_to_consider)
                    if early_out_to_count != 0:
                        # get deducted value
                        condition_type = slab.condition_type
                        basis_type = slab.basis_type

                        if condition_type == 'rule-based':
                            rbr_values = evaluate_RBR(slab, employee, early_out_to_count)
                            if None in rbr_values:
                                return None, 'Error: occurred while parsing early out mapping component'
                            if rbr_values:
                                leave_deduction_list = []
                                salary_deduction_tuple = None
                                for rbrval in rbr_values:
                                    if rbrval[0] == 'leave':
                                        leave_deduction_list.append(rbrval)
                                    else:
                                        salary_deduction_tuple = (rbrval[2], rbrval[3])
                                if salary_deduction_tuple:  # no salary deduction found but a list of leave deduction maybe found
                                    value, total_early_out_appearance = salary_deduction_tuple
                                    if basis_type == 'day-basis':
                                        total_deducted_value += (value * total_early_out_appearance)
                                    elif basis_type == 'salary-basis':
                                        total_deducted_value += value

                                deduction_list += leave_deduction_list
                    carry_over = total_early_out_appearance % slab.days_to_consider
                else:
                    carry_over = total_early_out_appearance

        return total_deducted_value, deduction_list

    def get_under_work_value(self, employee, start_date, end_date):
        employee_deduction_object = LeaveManage.objects.get(employee=employee)
        deduction_group = employee_deduction_object.deduction_group
        if deduction_group is None:
            return 0, []
        under_work_component = deduction_group.under_work_component
        if not under_work_component or under_work_component.deduction_component_type != 'under-work':
            return 0, []

        under_work_slab_objects = UnderWorkSlab.objects.filter(component=under_work_component)
        if not under_work_slab_objects.exists():
            return 0, []
        under_work_slab_context = {}

        for under_work_slab_object in under_work_slab_objects:
            under_work_slab_context[under_work_slab_object] = \
                under_work_slab_object.time if under_work_slab_object.unit == 'minute' else under_work_slab_object.time * 60

        sorted_under_work_slab_context = sorted(under_work_slab_context.items(), key=lambda x: x[1])
        sorted_under_work_slab_appearance_counter_context = {}
        for data, slab_value in sorted_under_work_slab_context:
            sorted_under_work_slab_appearance_counter_context[data] = 0
        total_under_work = 0

        processing_date = start_date
        while processing_date <= end_date:
            if not ScheduleRecord.objects.filter(employee=employee, date=processing_date).exists():
                return None, 'Error: Attendance Record does not exist for the date: ' + str(processing_date)
            record = ScheduleRecord.objects.get(employee=employee, date=processing_date)
            if not record.is_weekend or record.is_holiday:
                if not (record.is_working_day and not record.dailyrecord.is_present and not record.dailyrecord.is_leave_paid):
                    # employee is present for the day
                    if record.dailyrecord.under_work:
                        under_work_value = int(record.dailyrecord.under_work_value / 60)
                        total_under_work += 1
                        got_slab = False
                        for data, slab_value in sorted_under_work_slab_context:
                            if under_work_value <= slab_value:
                                sorted_under_work_slab_appearance_counter_context[data] += 1
                                got_slab = True
                                break

                        if not got_slab:
                            sorted_under_work_slab_appearance_counter_context[sorted_under_work_slab_context[-1][0]] += 1

            processing_date = processing_date + timedelta(days=1)  # date increment
        # loop ends

        dec_sorted_under_work_slab_appearance_counter_context = \
            sorted(sorted_under_work_slab_appearance_counter_context.items(),
                   key=lambda x: x[0].time if x[0].unit == 'minute' else x[0].time * 60, reverse=True)

        deduction_list = []
        total_deducted_value = 0
        if total_under_work > 0:
            carry_over = 0
            for slab, under_work_appearance in dec_sorted_under_work_slab_appearance_counter_context:
                total_under_work_appearance = under_work_appearance + carry_over
                if slab.days_to_consider > 0:
                    under_work_to_count = int(total_under_work_appearance / slab.days_to_consider)
                    if under_work_to_count != 0:
                        # get deducted value
                        condition_type = slab.condition_type
                        basis_type = slab.basis_type

                        if condition_type == 'rule-based':
                            rbr_values = evaluate_RBR(slab, employee, under_work_to_count)
                            if None in rbr_values:
                                return None, 'Error: occurred while parsing under-work mapping component'
                            if rbr_values:
                                leave_deduction_list = []
                                salary_deduction_tuple = None
                                for rbrval in rbr_values:
                                    if rbrval[0] == 'leave':
                                        leave_deduction_list.append(rbrval)
                                    else:
                                        salary_deduction_tuple = (rbrval[2], rbrval[3])
                                if salary_deduction_tuple:  # no salary deduction found but a list of leave deduction maybe found
                                    value, total_under_work_appearance = salary_deduction_tuple
                                    if basis_type == 'day-basis':
                                        total_deducted_value += (value * total_under_work_appearance)
                                    elif basis_type == 'salary-basis':
                                        total_deducted_value += value

                                deduction_list += leave_deduction_list
                    carry_over = total_under_work_appearance % slab.days_to_consider
                else:
                    carry_over = total_under_work_appearance

        return total_deducted_value, deduction_list

    def post(self, request, *args, **kwargs):
        FORCEFULLY_CHANGED_COMPONENTS.clear()
        context = {
            'permissions': self.get_current_user_permission_list(),
            'org_items_list': get_organizational_structure()
        }
        form = SearchForm(request.POST)
        context['form'] = form

        if not form.is_valid():
            messages.error(request, "Invalid Request")
            return render(request, self.template_name, {**context})

        if not form.my_is_valid():
            messages.error(request, "End date must be greater than start date")
            return render(request, self.template_name, {**context})

        employee = request.POST.get('employee')
        company = request.POST.get('company')
        division = request.POST.get('division')
        department = request.POST.get('department')
        business_unit = request.POST.get('business_unit')
        branch = request.POST.get('branch')
        schedule = request.POST.get('schedule')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        successful_processed_list = []
        unsuccessful_processed_list = []

        if employee:
            if EmployeeIdentification.objects.filter(employee_id=employee).exists():
                selected_employee = EmployeeIdentification.objects.get(employee_id=employee)

                processed, message = self.check_process_salary(selected_employee, start_date, end_date)
                if processed is None:
                    unsuccessful_processed_list.append(str(selected_employee)+': '+message)
                else:
                    successful_processed_list.append(processed)
                    # show the list of unsuccessful employee salary processed
            else:
                messages.error(request, "Invalid Employee ID")
                return render(request, self.template_name, {**context})
        else:
            employees = EmployeeIdentification.objects.all()
            if company:
                employees = employees.filter(employee_job_informations__company=company)
            if division:
                employees = employees.filter(employee_job_informations__division=division)
            if department:
                employees = employees.filter(employee_job_informations__department=department)
            if business_unit:
                employees = employees.filter(employee_job_informations__business_unit=business_unit)
            if branch:
                employees = employees.filter(employee_job_informations__branch=branch)
            if schedule:
                employees = employees.filter(employee_attendance__schedule_type=schedule)

            for employee in employees:
                processed, message = self.check_process_salary(employee, start_date, end_date)
                if processed is None:
                    unsuccessful_processed_list.append(str(employee)+': '+message)
                else:
                    successful_processed_list.append(processed)

        forcefully_changed_components = SalaryGroupComponent.objects.filter(id__in=FORCEFULLY_CHANGED_COMPONENTS)
        for component in forcefully_changed_components:  # type: SalaryGroupComponent
            component.variable.formulae.all().delete()

        FORCEFULLY_CHANGED_COMPONENTS.clear()

        context['unsuccessful_processed_list'] = \
            unsuccessful_processed_list if unsuccessful_processed_list.__len__() > 0 else None
        context['successful_processed_list'] = \
            successful_processed_list if successful_processed_list.__len__() > 0 else None

        return render(request, self.template_name, context)

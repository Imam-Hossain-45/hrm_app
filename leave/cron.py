from leave.models import LeaveRemaining
from datetime import datetime
from leave.views.process import convert_time_unit_into_seconds
def get_leave_credit(emp, leave):
    leave_manage = emp.leavemanage_set.get(leave_group__leave=leave)
    leave_settings = leave_manage.leave_group.group_settings.get(leave_name=leave)
    in_seconds = convert_time_unit_into_seconds(leave, leave_settings.leave_credit)
    return in_seconds


def leaveCron(frequency_num, frequency_unit):
    leave_remain_qs = LeaveRemaining.objects
    leave_remain_obj = leave_remain_qs.filter(status=True, leave__available_frequency_number=frequency_num,
                                              leave__available_frequency_unit=frequency_unit)

    leave_remain_obj.update(status=False, leave_avail_date=datetime.now())
    for leave_remain in leave_remain_obj:
        leave_remain_qs.create(employee=leave_remain.employee, status=True, leave=leave_remain.leave,
                               remaining_in_seconds=get_leave_credit(leave_remain.employee, leave_remain.leave))

    return True

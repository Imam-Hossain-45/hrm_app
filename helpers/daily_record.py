from datetime import datetime, timedelta

from django.db.models import Q

from attendance.models import ScheduleRecord, TimeTableRecord, BreakTimeRecord, DailyRecord
from employees.models import Attendance, JobInformation
from leave.models import LeaveAvail


def save_data(data):
    is_leave = False
    is_leave_paid = False
    leave_master = None
    break_duration = ''
    in_time = None
    out_time = None
    out_date = None
    working_hour = 0
    working_hour_unit = None
    is_working_day = False
    is_weekend = True
    is_holiday = False

    date_difference = data['range_end_date'] - data['range_start_date']
    for i in range(date_difference.days + 1):
        date = data['range_start_date'] + timedelta(days=i)

        if data['c_end_date'] > date >= data['c_start_date']:
            if date.strftime('%A') in data['calendar_m_workday']:
                is_working_day = True
                is_weekend = False

            if data['attendance'].schedule_type not in ['', None]:
                if data['attendance'].schedule_type.schedule_type == 'flexible':
                    schedule_day = data['attendance'].schedule_type.flexible_schedule.filter(
                        days__name=date.strftime('%A'))
                    if schedule_day.exists():
                        is_working_day = True
                        is_weekend = False
                        working_hour = schedule_day[0].working_hour
                        working_hour_unit = schedule_day[0].working_hour_unit
                    else:
                        is_working_day = False
                        is_weekend = True

                else:
                    schedule_day = data['attendance'].schedule_type.timetable_model.filter(
                        days__name=date.strftime('%A'))
                    if schedule_day.exists():
                        is_working_day = True
                        is_weekend = False

                        if data['attendance'].schedule_type.schedule_type == 'hourly':
                            in_time = schedule_day[0].in_time
                            out_time = schedule_day[0].out_time
                            if in_time < out_time:
                                out_date = date + timedelta(days=1)
                            else:
                                out_date = date
                        elif data['attendance'].schedule_type.schedule_type == 'variable_roster':
                            in_time = None
                            out_time = None
                        else:
                            in_time = schedule_day[0].in_time
                            out_time = schedule_day[0].out_time
                            if in_time not in ['', None] and out_time not in ['', None]:
                                if in_time > out_time:
                                    out_date = date + timedelta(days=1)
                                else:
                                    out_date = date

                            # get data from break time table of schedule
                            break_duration = schedule_day[0].breaktime_model.all()
                    else:
                        is_working_day = False
                        is_weekend = True

            avail_leave = LeaveAvail.objects.filter(employee_id=data['employee']).filter(
                Q(start_date__lte=date) & Q(end_date__gte=date))

            if data['attendance'].calendar_master.holiday_group:
                holiday_group = data['attendance'].calendar_master.holiday_group

                try:
                    holiday_group.holiday.get(start_date__lte=date, end_date__gte=date)
                    is_holiday = True
                    is_working_day = False
                    working_hour = 0
                    working_hour_unit = None
                    if avail_leave.exists():
                        is_leave = True
                        is_leave_paid = avail_leave[0].avail_leave.paid
                        leave_master = avail_leave[0].avail_leave
                        leave_credit = avail_leave[0].credit_seconds
                        if working_hour > 0:
                            if working_hour_unit == 'hour':
                                working_hour = working_hour - \
                                               (leave_credit / 3600)
                            else:
                                working_hour = working_hour - \
                                               (leave_credit / 60)
                            if working_hour < 0:
                                working_hour = 0
                except Exception as e:
                    is_holiday = False

            try:
                ScheduleRecord.objects.get(employee_id=data['employee'], date=date)
            except:
                schedule_update, schedule_create = ScheduleRecord.objects. \
                    update_or_create(employee_id=data['employee'], date=date,
                                     defaults={'is_weekend': is_weekend, 'is_working_day': is_working_day,
                                               'is_holiday': is_holiday, 'is_leave': is_leave,
                                               'working_hour': working_hour, 'working_hour_unit': working_hour_unit
                                               })

                schedule_record = schedule_update
                time_update, time_create = TimeTableRecord.objects.update_or_create(schedule_record=schedule_record,
                                                                                    defaults={'in_time': in_time,
                                                                                              'out_time': out_time,
                                                                                              'out_date': out_date})
                time_record = time_update

                if break_duration not in ['', None]:
                    break_qs = BreakTimeRecord.objects
                    break_qs.filter(timetable_record=time_record).delete()
                    for b in break_duration:
                        if in_time > b.break_start:
                            break_start_date = date + timedelta(days=1)
                        else:
                            break_start_date = date
                        if in_time > b.break_end:
                            break_end_date = date + timedelta(days=1)
                        else:
                            break_end_date = date
                        break_qs.create(timetable_record=time_record, break_start=b.break_start,
                                        break_end=b.break_end,
                                        break_start_date=break_start_date,
                                        break_end_date=break_end_date)

                DailyRecord.objects.update_or_create(
                    schedule_record=schedule_record, defaults={
                        'is_leave_paid': is_leave_paid,
                        'leave_master': leave_master,
                    })


def set_daily_record(data):

    """
        Save data in ScheduleRecord
        Save data in DailyRecord
        Save data in TimeTableRecord
        Save data in BreakTimeRecord
    """

    try:
        attendance = Attendance.objects.get(employee_id=data['employee'])

        if attendance.calendar_master not in ['', None]:

            calendar_m_start = attendance.calendar_master.effective_start_date
            calendar_m_end = attendance.calendar_master.effective_end_date
            calendar_m_workday = attendance.calendar_master.get_workday_display()

            if calendar_m_start not in ['', None] and calendar_m_end not in ['', None]:
                c_start_date = datetime.strptime(str(calendar_m_start), '%Y-%m-%d').date()
                c_end_date = datetime.strptime(str(calendar_m_end), '%Y-%m-%d').date()
                date = data['date']

                """" 
                check any record exists or not
                if not record exist save data from joining date                
                """

                schedule_record_qs = ScheduleRecord.objects.filter(employee_id=data['employee'])
                if schedule_record_qs.count() == 0:
                    job_information_obj = JobInformation.objects.filter(employee_id=data['employee']).last()

                    data = {
                        'employee': data['employee'],
                        'c_start_date': c_start_date,
                        'c_end_date': c_end_date,
                        'range_start_date': job_information_obj.date_of_joining,
                        'range_end_date': date,
                        'calendar_m_workday': calendar_m_workday,
                        'attendance': attendance,
                    }
                    save_data(data)
                else:
                    # check previous data exists or not
                    try:
                        schedule_record_qs.get(date=date-timedelta(days=1))
                        data = {
                            'employee': data['employee'],
                            'c_start_date': c_start_date,
                            'c_end_date': c_end_date,
                            'range_start_date': date,
                            'range_end_date': date + timedelta(days=1),
                            'calendar_m_workday': calendar_m_workday,
                            'attendance': attendance,
                        }
                        save_data(data)
                    except:
                        latest_data = schedule_record_qs.latest('date').date

                        if latest_data < date:
                            data = {
                                'employee': data['employee'],
                                'c_start_date': c_start_date,
                                'c_end_date': c_end_date,
                                'range_start_date': latest_data + timedelta(days=1),
                                'range_end_date': date,
                                'calendar_m_workday': calendar_m_workday,
                                'attendance': attendance,
                            }
                            save_data(data)

    except Exception as e:
        print(e)
        raise e

    return True

# Generated by Django 2.2.1 on 2019-11-19 07:16

from django.db import migrations, models
import django.db.models.deletion
import leave.validators
import multiselectfield.db.fields


def populate_days(apps, schema_editor):
    Days = apps.get_model('attendance', 'Days')
    Days.objects.bulk_create([
        Days(name='Saturday'),
        Days(name='Sunday'),
        Days(name='Monday'),
        Days(name='Tuesday'),
        Days(name='Wednesday'),
        Days(name='Thursday'),
        Days(name='Friday')
    ])


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cimbolic', '0008_auto_20191013_2347'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendanceBreak',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('break_start', models.TimeField(blank=True, null=True)),
                ('break_start_date', models.DateField(blank=True, null=True)),
                ('break_end', models.TimeField(blank=True, null=True)),
                ('break_end_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AttendanceData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(null=True)),
                ('in_time', models.TimeField(blank=True, null=True)),
                ('out_time', models.TimeField(blank=True, null=True)),
                ('out_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BreakTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('break_start', models.TimeField()),
                ('break_end', models.TimeField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CalendarMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('shortcode', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('effective_start_date', models.DateField()),
                ('effective_end_date', models.DateField()),
                ('workday', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], max_length=13, null=True)),
                ('status', models.CharField(blank=True, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DailyRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(null=True)),
                ('daily_working_seconds', models.IntegerField(default=0)),
                ('is_overtime', models.BooleanField(default=False)),
                ('daily_overtime_seconds', models.IntegerField(default=0)),
                ('late', models.BooleanField(default=False)),
                ('late_value', models.IntegerField(default=0)),
                ('early', models.BooleanField(default=False)),
                ('early_out_value', models.IntegerField(default=0)),
                ('under_work', models.BooleanField(default=False)),
                ('under_work_value', models.IntegerField(default=0)),
                ('is_weekend', models.BooleanField(default=False)),
                ('is_holiday', models.BooleanField(default=False)),
                ('is_working_day', models.BooleanField(default=False)),
                ('is_present', models.BooleanField(default=False)),
                ('is_leave', models.BooleanField(default=False)),
                ('is_leave_paid', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Days',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=20)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RunPython(populate_days),
        migrations.CreateModel(
            name='EarlyApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('early_out_time', models.TimeField(null=True)),
                ('reason_of_early_out', models.TextField(null=True)),
                ('attachment', models.FileField(blank=True, null=True, upload_to='early_out/', validators=[leave.validators.validate_file_extension])),
                ('status', models.CharField(blank=True, choices=[('pending', 'Pending'), ('declined', 'Declined'), ('approved', 'Approved')], default='pending', max_length=100, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EarlyApprovalComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('comment', models.TextField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FlexibleType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('working_hour', models.IntegerField(blank=True, default=0)),
                ('working_hour_unit', models.CharField(blank=True, choices=[('hour', 'Hour'), ('minute', 'Minute')], default='hour', max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HolidayGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('short_code', models.CharField(blank=True, max_length=20, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.BooleanField(blank=True, default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HolidayGroupMasterMembers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HolidayMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('short_code', models.CharField(blank=True, max_length=20, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('type', models.CharField(choices=[('festival', 'Festival'), ('national', 'National'), ('international', 'International')], default='festival', max_length=20)),
                ('status', models.BooleanField(blank=True, default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LateApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reason_of_late', models.TextField()),
                ('attachment', models.FileField(blank=True, null=True, upload_to='late_entry/', validators=[leave.validators.validate_file_extension])),
                ('status', models.CharField(blank=True, choices=[('pending', 'Pending'), ('declined', 'Declined'), ('approved', 'Approved')], default='pending', max_length=100, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OvertimeRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='rule name')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='short code')),
                ('description', models.CharField(blank=True, max_length=250)),
                ('buffer_duration', models.PositiveIntegerField(default=0, help_text='Minimum duration before overtime takes effect')),
                ('buffer_duration_unit', models.CharField(choices=[('m', 'Minute(s)'), ('h', 'Hour(s)')], default='m', max_length=1)),
                ('minimum_working_duration', models.PositiveIntegerField(default=1, help_text='Minimum duration to work for overtime to count')),
                ('minimum_working_duration_unit', models.CharField(choices=[('m', 'Minute(s)'), ('h', 'Hour(s)')], default='h', max_length=1)),
                ('taxable', models.BooleanField(help_text='Whether the overtime wage is taxable')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ScheduleMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('shortcode', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('schedule_type', models.CharField(choices=[('regular-fixed-time', 'Regular Fixed Time'), ('fixed-day', 'Fixed Day'), ('hourly', 'Hourly'), ('weekly', 'Weekly'), ('day', 'Day'), ('freelancing', 'Freelancing'), ('roaster', 'Roaster'), ('flexible', 'Flexible')], max_length=255, null=True)),
                ('roaster_type', models.CharField(blank=True, choices=[('fixed-roaster', 'Fixed Roaster'), ('variable-roaster', 'Variable Roaster')], max_length=255, null=True)),
                ('minimum_working_hour_per_day', models.IntegerField(blank=True, default=0)),
                ('minimum_working_hour_per_day_unit', models.CharField(blank=True, choices=[('hour', 'Hour'), ('minute', 'Minute')], default='hour', max_length=10)),
                ('maximum_working_hour_per_day', models.IntegerField(blank=True, default=0)),
                ('maximum_working_hour_per_day_unit', models.CharField(blank=True, choices=[('hour', 'Hour'), ('minute', 'Minute')], default='hour', max_length=10)),
                ('total_working_hour_per_day', models.IntegerField(blank=True, default=0)),
                ('total_working_hour_per_day_unit', models.CharField(blank=True, choices=[('hour', 'Hour'), ('minute', 'Minute')], default='hour', max_length=10)),
                ('total_working_hour_per_week', models.IntegerField(blank=True, default=0)),
                ('total_working_hour_per_week_unit', models.CharField(blank=True, choices=[('hour', 'Hour'), ('minute', 'Minute')], default='hour', max_length=10)),
                ('total_working_hour_per_month', models.IntegerField(blank=True, default=0)),
                ('total_working_hour_per_month_unit', models.CharField(blank=True, choices=[('hour', 'Hour'), ('minute', 'Minute')], default='hour', max_length=10)),
                ('working_day', models.IntegerField(blank=True, default=0)),
                ('vacation', models.IntegerField(blank=True, default=0)),
                ('status', models.CharField(blank=True, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WorkDaySchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('total_day_of_month', models.DecimalField(decimal_places=2, default=30, max_digits=10)),
                ('total_working_day_of_month', models.DecimalField(decimal_places=2, default=30, max_digits=10)),
                ('total_day_of_week', models.DecimalField(decimal_places=2, default=7, max_digits=10)),
                ('total_working_day_of_week', models.DecimalField(decimal_places=2, default=30, max_digits=10)),
                ('total_day_of_year', models.DecimalField(decimal_places=2, default=365, max_digits=10)),
                ('total_working_day_of_year', models.DecimalField(decimal_places=2, default=30, max_digits=10)),
                ('start_day_of_month', models.DecimalField(decimal_places=2, default=1, max_digits=10)),
                ('end_day_of_month', models.DecimalField(decimal_places=2, default=30, max_digits=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TimeTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('in_time', models.TimeField(blank=True, null=True)),
                ('out_time', models.TimeField(blank=True, null=True)),
                ('days', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.Days')),
                ('schedule_master', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='timetable_model', to='attendance.ScheduleMaster')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TimeDuration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('work_start', models.TimeField()),
                ('work_end', models.TimeField()),
                ('break_start', models.TimeField()),
                ('break_end', models.TimeField()),
                ('timetable', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='attendance.TimeTable')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='schedulemaster',
            name='days',
            field=models.ManyToManyField(through='attendance.TimeTable', to='attendance.Days'),
        ),
        migrations.AddField(
            model_name='schedulemaster',
            name='parent_schedule',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='attendance.ScheduleMaster'),
        ),
        migrations.CreateModel(
            name='OvertimeWageCalculationVariable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('enabled', models.BooleanField(default=False, help_text='Whether this method is enabled')),
                ('basis', models.CharField(choices=[('m', 'Minutely'), ('h', 'Hourly'), ('d', 'Daily'), ('s', 'Top of salary')], default='h', help_text='Scope type of the wage calculation (per hour, per day etc.)', max_length=1)),
                ('rule', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='variable_wage', to='attendance.OvertimeRule')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OvertimeWageCalculationRuleBased',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('enabled', models.BooleanField(default=False, help_text='Whether this method is enabled')),
                ('rule', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rule_based_wage', to='attendance.OvertimeRule')),
                ('variable', models.OneToOneField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='cimbolic.Variable')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OvertimeWageCalculationManual',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('enabled', models.BooleanField(default=False, help_text='Whether this method is enabled')),
                ('rule', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='manual_wage', to='attendance.OvertimeRule')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OvertimeWageCalculationFixedRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('enabled', models.BooleanField(default=False, help_text='Whether this method is enabled')),
                ('basis', models.CharField(choices=[('m', 'Minutely'), ('h', 'Hourly'), ('d', 'Daily'), ('s', 'Top of salary')], default='h', help_text='Scope type of the wage calculation (per hour, per day etc.)', max_length=1)),
                ('scope_value', models.PositiveIntegerField(blank=True, default=1, help_text='Scope value (per how many hours/days)')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, help_text='Fixed-rate amount', max_digits=10, null=True)),
                ('rule', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='fixed_rate_wage', to='attendance.OvertimeRule')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OvertimeDurationRestriction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('scope_value', models.PositiveIntegerField(help_text='Time period (scope) in which the restriction applies')),
                ('scope_unit', models.CharField(choices=[('d', 'Day(s)'), ('w', 'Week(s)'), ('m', 'Month(s)')], help_text='Unit of measurement of the scope (time period)', max_length=1)),
                ('maximum_duration', models.PositiveIntegerField(help_text='Maximum duration of OT allowed')),
                ('maximum_duration_unit', models.CharField(choices=[('m', 'Minute(s)'), ('h', 'Hour(s)'), ('d', 'Day(s)'), ('w', 'Week(s)')], help_text='Unit of duration', max_length=1)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=10)),
                ('rule', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='duration_restrictions', related_query_name='duration_restriction', to='attendance.OvertimeRule')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LateApprovalComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('comment', models.TextField(null=True)),
                ('late_entry', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='late_entry', to='attendance.LateApplication')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

# Generated by Django 2.2.1 on 2019-11-19 07:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('payroll', '0001_initial'),
        ('employees', '0001_initial'),
        ('setting', '0001_initial'),
        ('leave', '0001_initial'),
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='salarystructure',
            name='bonus_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payroll.BonusGroup'),
        ),
        migrations.AddField(
            model_name='salarystructure',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_salary_structure', to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='salarystructure',
            name='salary_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payroll.SalaryGroup'),
        ),
        migrations.AddField(
            model_name='retirement',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='reference',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='professionalcertificate',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='personal',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='payment',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='payment',
            name='employee_bank_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='setting.Bank'),
        ),
        migrations.AddField(
            model_name='othersdocuments',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='leavemanage',
            name='deduction_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_leave_deduction', to='payroll.DeductionGroup'),
        ),
        migrations.AddField(
            model_name='leavemanage',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='leavemanage',
            name='leave_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='leave.LeaveGroup'),
        ),
        migrations.AddField(
            model_name='leavemanage',
            name='overtime_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_overtime', to='attendance.OvertimeRule', verbose_name='Select Overtime'),
        ),
        migrations.AddField(
            model_name='languageproficiency',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='jobinformation',
            name='additional_report_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='additional_report_to', to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='jobinformation',
            name='business_unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='setting.BusinessUnit'),
        ),
        migrations.AddField(
            model_name='jobinformation',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='setting.Company'),
        ),
        migrations.AddField(
            model_name='jobinformation',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='setting.Department'),
        ),
        migrations.AddField(
            model_name='jobinformation',
            name='designation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='setting_designation', to='setting.Designation'),
        ),
        migrations.AddField(
            model_name='jobinformation',
            name='division',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='setting.Division'),
        ),
        migrations.AddField(
            model_name='jobinformation',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_job_information', related_query_name='employee_job_informations', to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='jobinformation',
            name='employment_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='setting.EmploymentType'),
        ),
        migrations.AddField(
            model_name='jobinformation',
            name='job_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='setting.JobStatus'),
        ),
        migrations.AddField(
            model_name='jobinformation',
            name='pay_grade',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payroll.PayGrade'),
        ),
        migrations.AddField(
            model_name='jobinformation',
            name='pay_scale',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payroll.PayScale'),
        ),
        migrations.AddField(
            model_name='jobinformation',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='setting.Project'),
        ),
        migrations.AddField(
            model_name='jobinformation',
            name='report_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='report_to', to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='family',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='endofcontract',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='employmenthistory',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='employment',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employment', related_query_name='employments', to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='emergencycontact',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='education',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='documents',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='calendar_master',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_calendar', to='attendance.CalendarMaster', verbose_name='Calendar'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_attendance', to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='schedule_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='attendance.ScheduleMaster'),
        ),
        migrations.AddField(
            model_name='asset',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='addressandcontact',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.EmployeeIdentification'),
        ),
        migrations.AlterUniqueTogether(
            name='training',
            unique_together={('employee', 'training_title')},
        ),
        migrations.AlterUniqueTogether(
            name='skill',
            unique_together={('employee', 'skill_name')},
        ),
        migrations.AlterUniqueTogether(
            name='professionalcertificate',
            unique_together={('employee', 'certificate_title')},
        ),
        migrations.AlterUniqueTogether(
            name='othersdocuments',
            unique_together={('employee', 'title')},
        ),
        migrations.AlterUniqueTogether(
            name='languageproficiency',
            unique_together={('employee', 'language')},
        ),
        migrations.AlterUniqueTogether(
            name='education',
            unique_together={('employee', 'degree')},
        ),
    ]
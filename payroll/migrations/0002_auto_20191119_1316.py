# Generated by Django 2.2.1 on 2019-11-19 07:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0002_auto_20191119_1316'),
        ('payroll', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='payscale',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pay_scale_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='payscale',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pay_scale_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='paygrade',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='grade_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='paygrade',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='grade_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lateslab',
            name='component',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='payroll.DeductionComponent'),
        ),
        migrations.AddField(
            model_name='latesetting',
            name='component',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='payroll.DeductionComponent'),
        ),
        migrations.AddField(
            model_name='employeevariablesalary',
            name='component',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.Component'),
        ),
        migrations.AddField(
            model_name='employeevariablesalary',
            name='salary_structure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.SalaryStructure'),
        ),
        migrations.AddField(
            model_name='employeesalary',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.EmployeeIdentification'),
        ),
        migrations.AddField(
            model_name='earlyoutslab',
            name='component',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='payroll.DeductionComponent'),
        ),
        migrations.AddField(
            model_name='earlyoutsetting',
            name='component',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='payroll.DeductionComponent'),
        ),
        migrations.AddField(
            model_name='deductiongroup',
            name='absent_component',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='group_absent_component', to='payroll.DeductionComponent'),
        ),
        migrations.AddField(
            model_name='deductiongroup',
            name='early_out_component',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='group_early_out_component', to='payroll.DeductionComponent'),
        ),
        migrations.AddField(
            model_name='deductiongroup',
            name='late_component',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='group_late_component', to='payroll.DeductionComponent'),
        ),
        migrations.AddField(
            model_name='deductiongroup',
            name='other_component',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='group_other_component', to='payroll.DeductionComponent'),
        ),
        migrations.AddField(
            model_name='deductiongroup',
            name='under_work_component',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='group_under_work_component', to='payroll.DeductionComponent'),
        ),
        migrations.AddField(
            model_name='bonusgroupcomponentmembers',
            name='component',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.BonusComponent'),
        ),
        migrations.AddField(
            model_name='bonusgroupcomponentmembers',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.BonusGroup'),
        ),
        migrations.AddField(
            model_name='bonusgroup',
            name='bonus_component',
            field=models.ManyToManyField(through='payroll.BonusGroupComponentMembers', to='payroll.BonusComponent'),
        ),
        migrations.AddField(
            model_name='absentsetting',
            name='component',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='payroll.DeductionComponent'),
        ),
    ]

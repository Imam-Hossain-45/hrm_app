# Generated by Django 2.2.1 on 2020-01-14 14:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0008_auto_20200101_1235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobinformation',
            name='business_unit',
            field=models.ForeignKey(blank=True, limit_choices_to={'status': 'active'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='setting.BusinessUnit'),
        ),
        migrations.AlterField(
            model_name='jobinformation',
            name='company',
            field=models.ForeignKey(limit_choices_to={'status': 'active'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='setting.Company'),
        ),
        migrations.AlterField(
            model_name='jobinformation',
            name='department',
            field=models.ForeignKey(blank=True, limit_choices_to={'status': 'active'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='setting.Department'),
        ),
        migrations.AlterField(
            model_name='jobinformation',
            name='designation',
            field=models.ForeignKey(blank=True, limit_choices_to={'status': 'active'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='setting_designation', to='setting.Designation'),
        ),
        migrations.AlterField(
            model_name='jobinformation',
            name='division',
            field=models.ForeignKey(blank=True, limit_choices_to={'status': 'active'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='setting.Division'),
        ),
        migrations.AlterField(
            model_name='jobinformation',
            name='employment_type',
            field=models.ForeignKey(blank=True, limit_choices_to={'status': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='setting.EmploymentType'),
        ),
        migrations.AlterField(
            model_name='jobinformation',
            name='job_status',
            field=models.ForeignKey(blank=True, limit_choices_to={'status': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='setting.JobStatus'),
        ),
        migrations.AlterField(
            model_name='jobinformation',
            name='pay_grade',
            field=models.ForeignKey(blank=True, limit_choices_to={'status': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payroll.PayGrade'),
        ),
        migrations.AlterField(
            model_name='jobinformation',
            name='pay_scale',
            field=models.ForeignKey(blank=True, limit_choices_to={'status': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payroll.PayScale'),
        ),
        migrations.AlterField(
            model_name='jobinformation',
            name='project',
            field=models.ForeignKey(blank=True, limit_choices_to={'status': 'active'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='setting.Project'),
        ),
        migrations.AlterField(
            model_name='salarystructure',
            name='bonus_group',
            field=models.ForeignKey(blank=True, limit_choices_to={'status': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payroll.BonusGroup'),
        ),
        migrations.AlterField(
            model_name='salarystructure',
            name='salary_group',
            field=models.ForeignKey(limit_choices_to={'status': 'active'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payroll.SalaryGroup'),
        ),
    ]

# Generated by Django 2.2.1 on 2019-11-20 13:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0002_auto_20191119_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_payment', to='employees.EmployeeIdentification'),
        ),
    ]
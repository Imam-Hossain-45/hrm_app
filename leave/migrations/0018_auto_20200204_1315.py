# Generated by Django 2.2.1 on 2020-02-04 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0017_leavegroupsettings_employee_can_apply'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leavegroupsettings',
            name='employee_can_apply',
            field=models.BooleanField(default=False),
        ),
    ]
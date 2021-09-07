# Generated by Django 2.2.1 on 2019-11-21 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_auto_20191119_1316'),
    ]

    operations = [
        migrations.AddField(
            model_name='overtimerule',
            name='default_calculation_unit',
            field=models.CharField(choices=[('m', 'Minute(s)'), ('h', 'Hour(s)')], default='m', max_length=1),
        ),
        migrations.AddField(
            model_name='overtimerule',
            name='tolerance_time',
            field=models.PositiveIntegerField(default=0, help_text='Helper for rounding the OT duration'),
        ),
    ]
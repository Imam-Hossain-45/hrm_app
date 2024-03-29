# Generated by Django 2.2.1 on 2020-02-06 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0018_auto_20200204_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leavemaster',
            name='fractional',
            field=models.BooleanField(default=False, help_text='Leave - that is a part of a day.', verbose_name='It a hourly Leave'),
        ),
        migrations.AlterField(
            model_name='leavemaster',
            name='fractional_time_unit',
            field=models.CharField(blank=True, choices=[('minutes', 'Minutes'), ('hours', 'Hours')], max_length=20, null=True, verbose_name='Time unit for hourly leave'),
        ),
    ]

# Generated by Django 2.2.1 on 2020-01-15 18:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0020_auto_20200115_1814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendarmaster',
            name='parent_calendar',
            field=models.ForeignKey(blank=True, limit_choices_to={'status': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='attendance.CalendarMaster'),
        ),
    ]

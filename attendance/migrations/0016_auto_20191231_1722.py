# Generated by Django 2.2.1 on 2019-12-31 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0015_overtimedurationrestriction_ot_segment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendarmaster',
            name='effective_end_date',
            field=models.DateField(blank=True),
        ),
    ]

# Generated by Django 2.2.1 on 2019-12-05 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0003_auto_20191122_0249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leavemaster',
            name='available_frequency_unit',
            field=models.CharField(choices=[('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year'), ('quarter', 'Quarter'), ('half_year', 'Half Year'), ('lifetime', 'Lifetime')], default='year', max_length=50, null=True, verbose_name='Available Frequency'),
        ),
        migrations.AlterField(
            model_name='leaverestriction',
            name='within_unit',
            field=models.CharField(choices=[('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year'), ('quarter', 'Quarter'), ('half_year', 'Half Year'), ('lifetime', 'Lifetime')], default='year', max_length=50),
        ),
    ]

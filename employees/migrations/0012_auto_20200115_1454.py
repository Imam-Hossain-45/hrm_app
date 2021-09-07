# Generated by Django 2.2.1 on 2020-01-15 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0011_auto_20200115_1451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employment',
            name='confirmation_after',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='employment',
            name='confirmation_after_unit',
            field=models.CharField(blank=True, choices=[('days', 'Days'), ('months', 'Months'), ('years', 'Years')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='employment',
            name='date_of_actual_confirmation',
            field=models.DateField(blank=True, null=True),
        ),
    ]
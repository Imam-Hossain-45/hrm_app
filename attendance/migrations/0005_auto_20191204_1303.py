# Generated by Django 2.2.1 on 2019-12-04 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0004_overtimewagecalculationrulebased_basis'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendarmaster',
            name='shortcode',
            field=models.CharField(max_length=255, null=True, unique=True),
        ),
    ]

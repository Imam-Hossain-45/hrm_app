# Generated by Django 2.2.1 on 2019-12-11 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0009_auto_20191211_1528'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyrecord',
            name='daily_pre_overtime_seconds',
            field=models.IntegerField(default=0),
        ),
    ]
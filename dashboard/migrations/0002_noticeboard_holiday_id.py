# Generated by Django 2.2.1 on 2020-02-24 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='noticeboard',
            name='holiday_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

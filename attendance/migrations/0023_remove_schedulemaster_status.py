# Generated by Django 2.2.1 on 2020-01-15 18:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0022_auto_20200115_1837'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedulemaster',
            name='status',
        ),
    ]

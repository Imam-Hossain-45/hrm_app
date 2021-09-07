# Generated by Django 2.2.1 on 2020-02-24 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0008_auto_20200219_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approval',
            name='status',
            field=models.CharField(blank=True, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('declined', 'Declined')], default='pending', max_length=10),
        ),
    ]

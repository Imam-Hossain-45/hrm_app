# Generated by Django 2.2.1 on 2020-01-15 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0015_auto_20200115_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='punching_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Punching ID'),
        ),
    ]

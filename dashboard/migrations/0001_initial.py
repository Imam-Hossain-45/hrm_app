# Generated by Django 2.2.1 on 2020-02-24 16:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NoticeBoard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notice', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.BooleanField(blank=True, default=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('published_datetime', models.DateTimeField(blank=True, null=True)),
                ('type', models.CharField(blank=True, choices=[('custom', 'Custom'), ('calendar', 'Calendar'), ('birthday', 'Birthday')], default='calendar', max_length=11)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

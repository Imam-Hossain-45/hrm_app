# Generated by Django 2.2.1 on 2019-11-19 13:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0002_leaveapprovalcomment_user'),
        ('payroll', '0004_absentsettingrbr'),
    ]

    operations = [
        migrations.CreateModel(
            name='LateSlabRBR',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('priority', models.PositiveIntegerField()),
                ('condition', models.TextField(default='NULL')),
                ('rule', models.TextField()),
                ('deduct_from', models.CharField(choices=[('s', 'Salary'), ('l', 'Leave')], default='l', max_length=1)),
                ('late_slab', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rbr_set', related_query_name='rbr', to='payroll.LateSlab')),
                ('leave_component', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='leave.LeaveMaster')),
                ('salary_component', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='payroll.Component')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

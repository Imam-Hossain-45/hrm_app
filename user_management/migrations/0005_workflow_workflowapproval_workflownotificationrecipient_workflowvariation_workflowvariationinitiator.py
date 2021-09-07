# Generated by Django 2.2.1 on 2019-11-20 12:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('user_management', '0004_user_employee'),
    ]

    operations = [
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(blank=True, choices=[('undefined', 'Undefined'), ('defined', 'Defined')], default='undefined', max_length=10)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WorkflowVariation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('workflow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_management.Workflow')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WorkflowVariationLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('level', models.PositiveIntegerField()),
                ('workflow_variation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_management.WorkflowVariation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WorkflowVariationInitiator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('initiator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
                ('workflow_variation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_management.WorkflowVariation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WorkflowNotificationRecipient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notification_recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
                ('workflow_variation_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_management.WorkflowVariationLevel')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WorkflowApproval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('next_approval_operator', models.CharField(blank=True, choices=[('and', 'And'), ('or', 'Or')], max_length=3, null=True)),
                ('approved_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
                ('workflow_variation_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_management.WorkflowVariationLevel')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

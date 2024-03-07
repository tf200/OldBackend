# Generated by Django 5.0.1 on 2024-03-07 15:34

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0034_temporaryfile_and_more'),
        ('employees', '0024_alter_clientgoals_report'),
    ]

    operations = [
        migrations.CreateModel(
            name='TemporaryFile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to='temporary_files/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Incident',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_reported', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_of_incident', models.DateField()),
                ('time_of_incident', models.TimeField()),
                ('location', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('action_taken', models.TextField(blank=True, null=True)),
                ('follow_up_required', models.BooleanField(default=False)),
                ('follow_up_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Reported', 'Reported'), ('Under Investigation', 'Under Investigation'), ('Resolved', 'Resolved'), ('Closed', 'Closed')], default='Reported', max_length=100)),
                ('involved_children', models.ManyToManyField(related_name='incidents', to='client.clientdetails')),
                ('reported_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reported_incidents', to='employees.employeeprofile')),
            ],
            options={
                'verbose_name': 'Incident',
                'verbose_name_plural': 'Incidents',
            },
        ),
    ]

# Generated by Django 5.0.1 on 2024-02-06 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0012_alter_progressreport_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientemergencycontact',
            name='auto_reports',
            field=models.BooleanField(default=False),
        ),
    ]

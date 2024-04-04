# Generated by Django 5.0.1 on 2024-04-04 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planning", "0004_appointment_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="status",
            field=models.CharField(
                choices=[
                    ("scheduled", "Scheduled"),
                    ("completed", "Completed"),
                    ("canceled", "Canceled"),
                ],
                default="scheduled",
            ),
        ),
    ]

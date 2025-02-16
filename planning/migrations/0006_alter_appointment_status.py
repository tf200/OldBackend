# Generated by Django 5.0.1 on 2024-04-04 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planning", "0005_alter_appointment_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("scheduled", "Scheduled"),
                    ("finished", "Finished"),
                    ("canceled", "Canceled"),
                ],
                default="scheduled",
            ),
        ),
    ]

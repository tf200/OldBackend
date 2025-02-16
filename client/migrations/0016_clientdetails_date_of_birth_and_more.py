# Generated by Django 5.0.1 on 2024-02-08 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0015_remove_feedback_client_remove_measurement_client_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="clientdetails",
            name="date_of_birth",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="clientemergencycontact",
            name="relation_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Primary-Relationship", "Primary-Relationship"),
                    ("Secondary-Relationship", "Secondary-Relationship"),
                ],
                max_length=50,
                null=True,
            ),
        ),
    ]

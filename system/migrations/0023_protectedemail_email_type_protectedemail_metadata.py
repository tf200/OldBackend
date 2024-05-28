# Generated by Django 5.0.1 on 2024-05-28 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("system", "0022_protectedemail"),
    ]

    operations = [
        migrations.AddField(
            model_name="protectedemail",
            name="email_type",
            field=models.CharField(
                choices=[
                    ("incident_report", "Incident Report"),
                    ("medical_report", "Medical Report"),
                ],
                default="incident_report",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="protectedemail",
            name="metadata",
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]

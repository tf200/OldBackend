# Generated by Django 5.0.1 on 2024-05-20 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0098_alter_careplan_options_alter_temporaryfile_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="clientdocuments",
            name="label",
            field=models.CharField(
                choices=[
                    ("registration_form", "Registration Form"),
                    ("intake_form", "Intake Form"),
                    ("consent_form", "Consent Form"),
                    ("risk_assessment", "Risk Assessment"),
                    ("self_reliance_matrix", "Self-reliance Matrix"),
                    ("force_inventory", "Force Inventory"),
                    ("care_plan", "Care Plan"),
                    ("signaling_plan", "Signaling Plan"),
                    ("cooperation_agreement", "Cooperation Agreement"),
                ],
                default="registration_form",
                max_length=100,
            ),
        ),
    ]

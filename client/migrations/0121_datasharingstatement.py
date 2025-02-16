# Generated by Django 5.0.1 on 2024-05-31 13:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0120_clientemergencycontact_uuid"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataSharingStatement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("youth_name", models.CharField(max_length=255)),
                ("date_of_birth", models.DateField()),
                ("parent_guardian_name", models.CharField(max_length=255)),
                ("address", models.TextField()),
                ("youth_care_institution", models.CharField(max_length=255)),
                ("data_description", models.TextField()),
                ("data_purpose", models.TextField()),
                ("third_party_names", models.TextField()),
                ("statement", models.TextField()),
                ("parent_guardian_signature_name", models.CharField(max_length=255)),
                ("parent_guardian_signature", models.CharField(max_length=255)),
                ("parent_guardian_signature_date", models.DateField()),
                ("juvenile_name", models.CharField(blank=True, max_length=255, null=True)),
                ("juvenile_signature", models.CharField(blank=True, max_length=255, null=True)),
                ("juvenile_signature_date", models.DateField(blank=True, null=True)),
                ("institution_representative_name", models.CharField(max_length=255)),
                ("institution_representative_signature", models.CharField(max_length=255)),
                ("institution_representative_signature_date", models.DateField()),
                ("contact_person_name", models.CharField(max_length=255)),
                ("contact_phone_number", models.CharField(max_length=20)),
                ("contact_email", models.EmailField(max_length=254)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="data_sharing_statements",
                        to="client.clientdetails",
                    ),
                ),
            ],
        ),
    ]

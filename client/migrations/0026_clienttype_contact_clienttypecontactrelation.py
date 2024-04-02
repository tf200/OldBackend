# Generated by Django 5.0.1 on 2024-03-04 12:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0025_delete_clientmedication"),
    ]

    operations = [
        migrations.CreateModel(
            name="ClientType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "types",
                    models.CharField(
                        choices=[
                            ("main_provider", "Main Provider"),
                            ("local_authority", "Local Authority"),
                            ("particular_party", "Particular Party"),
                            ("healthcare_institution", "Healthcare Institution"),
                        ],
                        max_length=50,
                    ),
                ),
                ("name", models.CharField(max_length=20)),
                ("address", models.CharField(blank=True, max_length=200, null=True)),
                ("postal_code", models.CharField(blank=True, max_length=20, null=True)),
                ("place", models.CharField(blank=True, max_length=20, null=True)),
                ("land", models.CharField(blank=True, max_length=20, null=True)),
                ("KVKnumber", models.CharField(blank=True, max_length=20, null=True)),
                ("BTWnumber", models.CharField(blank=True, max_length=20, null=True)),
                ("phone_number", models.CharField(blank=True, max_length=20, null=True)),
                ("client_number", models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Contact",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("phone_number", models.CharField(max_length=20)),
                ("email", models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name="ClientTypeContactRelation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "client_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="client.clienttype"
                    ),
                ),
                (
                    "contact",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="client.contact"
                    ),
                ),
            ],
        ),
    ]

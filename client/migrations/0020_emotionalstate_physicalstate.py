# Generated by Django 5.0.1 on 2024-02-08 17:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0019_alter_clientemergencycontact_relation_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmotionalState",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("severity", models.CharField(blank=True, max_length=50, null=True)),
                ("date", models.DateTimeField()),
                ("state_description", models.TextField()),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="client_emotional",
                        to="client.clientdetails",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PhysicalState",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("severity", models.CharField(blank=True, max_length=50, null=True)),
                ("date", models.DateTimeField()),
                ("symptoms", models.TextField()),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="client_physical",
                        to="client.clientdetails",
                    ),
                ),
            ],
        ),
    ]

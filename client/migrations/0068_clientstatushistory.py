# Generated by Django 5.0.1 on 2024-04-24 12:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0067_alter_clientdetails_status_alter_contract_client_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ClientStatusHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("In Care", "In Care"),
                            ("On Waiting List", "On Waiting List"),
                            ("Out Of Care", "Out Of Care"),
                        ]
                    ),
                ),
                ("start_date", models.DateTimeField(auto_now_add=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="status_history",
                        to="client.clientdetails",
                    ),
                ),
            ],
        ),
    ]

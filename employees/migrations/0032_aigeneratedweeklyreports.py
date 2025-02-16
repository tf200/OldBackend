# Generated by Django 5.0.1 on 2024-03-26 22:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0031_remove_clientgoals_rating_goalsreport_created_at_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="AiGeneratedWeeklyReports",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("report_text", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "goal",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="employees.clientgoals",
                    ),
                ),
            ],
        ),
    ]

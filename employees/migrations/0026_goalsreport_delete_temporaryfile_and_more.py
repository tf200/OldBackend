# Generated by Django 5.0.1 on 2024-03-08 14:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0025_temporaryfile_incident"),
    ]

    operations = [
        migrations.CreateModel(
            name="GoalsReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("tiltle", models.CharField(max_length=100)),
                ("report_text", models.TextField()),
            ],
        ),
        migrations.DeleteModel(
            name="TemporaryFile",
        ),
        migrations.RemoveField(
            model_name="clientgoals",
            name="report",
        ),
        migrations.AddField(
            model_name="goalsreport",
            name="goal",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="goals_report",
                to="employees.clientgoals",
            ),
        ),
    ]

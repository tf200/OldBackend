# Generated by Django 5.0.1 on 2024-02-01 10:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0006_rename_firt_name_clientdetails_first_name_and_more"),
        ("employees", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Assignment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("start_datetime", models.DateTimeField()),
                ("end_datetime", models.DateTimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Confirmed", "Confirmed"),
                            ("Pending", "Pending"),
                            ("Cancelled", "Cancelled"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assigned_employees",
                        to="client.clientdetails",
                    ),
                ),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignments",
                        to="employees.employeeprofile",
                    ),
                ),
            ],
        ),
    ]

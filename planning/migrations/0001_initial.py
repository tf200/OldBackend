# Generated by Django 5.0.1 on 2024-02-20 10:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("client", "0024_alter_clientdetails_status"),
        ("employees", "0019_remove_employeeprofile_graduation_year_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Appointment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "appointment_type",
                    models.CharField(
                        choices=[
                            ("meeting", "Meeting"),
                            ("work", "Work with Client"),
                            ("other", "Other"),
                        ],
                        max_length=50,
                    ),
                ),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                ("location", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "clients",
                    models.ManyToManyField(
                        related_name="client_appointments", to="client.clientdetails"
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_appointments",
                        to="employees.employeeprofile",
                    ),
                ),
                (
                    "employees",
                    models.ManyToManyField(
                        related_name="employee_appointments", to="employees.employeeprofile"
                    ),
                ),
                (
                    "modified_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="modified_appointments",
                        to="employees.employeeprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AppointmentAttachment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("file", models.FileField(upload_to="appointment_attachments/")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "name",
                    models.CharField(
                        blank=True, help_text="Optional name for the file", max_length=255
                    ),
                ),
                (
                    "appointment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="planning.appointment",
                    ),
                ),
            ],
        ),
    ]

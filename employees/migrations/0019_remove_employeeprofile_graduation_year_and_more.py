# Generated by Django 5.0.1 on 2024-02-14 08:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0018_remove_employeeprofile_certifications_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="employeeprofile",
            name="graduation_year",
        ),
        migrations.RemoveField(
            model_name="employeeprofile",
            name="highest_education",
        ),
        migrations.RemoveField(
            model_name="employeeprofile",
            name="university",
        ),
        migrations.CreateModel(
            name="Education",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("institution_name", models.CharField(max_length=255)),
                ("degree", models.CharField(max_length=100)),
                ("field_of_study", models.CharField(max_length=100)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="education_history",
                        to="employees.employeeprofile",
                    ),
                ),
            ],
        ),
    ]

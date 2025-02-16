# Generated by Django 5.0.1 on 2024-01-30 16:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="EmployeeProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("address", models.TextField(blank=True, null=True)),
                ("position", models.CharField(max_length=100)),
                ("department", models.CharField(max_length=100)),
                ("highest_education", models.CharField(max_length=100)),
                ("university", models.CharField(blank=True, max_length=100, null=True)),
                ("graduation_year", models.IntegerField(blank=True, null=True)),
                (
                    "certifications",
                    models.TextField(blank=True, help_text="List of certifications", null=True),
                ),
                (
                    "experience",
                    models.TextField(
                        blank=True, help_text="List of relevant work experiences", null=True
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

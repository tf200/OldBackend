# Generated by Django 5.0.1 on 2024-03-11 09:14

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0034_temporaryfile_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Invoice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "invoice_number",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("issue_date", models.DateField(auto_now_add=True)),
                ("due_date", models.DateField()),
                (
                    "pre_vat_total",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                ("vat_rate", models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ("vat_amount", models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                (
                    "total_amount",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("outstanding", "Outstanding"),
                            ("partially_paid", "Partially Paid"),
                            ("paid", "Paid"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invoices",
                        to="client.contract",
                    ),
                ),
            ],
        ),
    ]

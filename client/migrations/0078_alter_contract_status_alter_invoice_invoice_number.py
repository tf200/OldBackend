# Generated by Django 5.0.1 on 2024-04-27 11:51

import client.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0077_rename_care_plan_domaingoal_domain"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contract",
            name="status",
            field=models.CharField(
                choices=[
                    ("approved", "Approved"),
                    ("draft", "Draft"),
                    ("terminated", "Terminated"),
                    ("stoped", "Stopped"),
                ],
                default="draft",
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="invoice_number",
            field=models.CharField(
                db_index=True,
                default=client.models.generate_invoice_id,
                editable=False,
                max_length=10,
                unique=True,
            ),
        ),
    ]

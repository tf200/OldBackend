# Generated by Django 5.0.1 on 2024-04-24 10:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0066_alter_invoice_total_amount"),
    ]

    operations = [
        migrations.AlterField(
            model_name="clientdetails",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("In Care", "In Care"),
                    ("On Waiting List", "On Waiting List"),
                    ("Out Of Care", "Out Of Care"),
                ],
                default="On Waiting List",
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="contract",
            name="client",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="contracts",
                to="client.clientdetails",
            ),
        ),
        migrations.AlterField(
            model_name="contract",
            name="sender",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="contracts",
                to="client.sender",
            ),
        ),
    ]

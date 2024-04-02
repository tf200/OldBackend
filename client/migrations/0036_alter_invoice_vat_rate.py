# Generated by Django 5.0.1 on 2024-03-11 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0035_invoice"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="vat_rate",
            field=models.DecimalField(decimal_places=2, default=20, max_digits=5),
        ),
    ]

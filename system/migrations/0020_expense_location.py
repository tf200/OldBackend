# Generated by Django 5.0.1 on 2024-05-05 08:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0009_location_capacity"),
        ("system", "0019_expense_tax"),
    ]

    operations = [
        migrations.AddField(
            model_name="expense",
            name="location",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="expenses",
                to="authentication.location",
            ),
        ),
    ]

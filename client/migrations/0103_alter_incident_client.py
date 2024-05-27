# Generated by Django 5.0.1 on 2024-05-24 09:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0102_incident"),
    ]

    operations = [
        migrations.AlterField(
            model_name="incident",
            name="client",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="incidents",
                to="client.clientdetails",
            ),
        ),
    ]

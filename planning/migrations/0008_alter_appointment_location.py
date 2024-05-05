# Generated by Django 5.0.1 on 2024-05-05 09:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0009_location_capacity"),
        ("planning", "0007_alter_appointment_appointment_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="location",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="appointments",
                to="authentication.location",
            ),
            preserve_default=False,
        ),
    ]

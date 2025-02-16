# Generated by Django 5.0.1 on 2024-03-05 10:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0030_clientdetails_sender_delete_clientsender"),
    ]

    operations = [
        migrations.AlterField(
            model_name="clientdetails",
            name="sender",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="clientsender",
                to="client.clienttype",
            ),
        ),
    ]

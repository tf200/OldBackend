# Generated by Django 5.0.1 on 2024-05-24 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0104_alter_incident_options_incident_soft_delete"),
    ]

    operations = [
        migrations.AddField(
            model_name="incident",
            name="client_options",
            field=models.JSONField(default=list),
        ),
    ]

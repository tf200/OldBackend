# Generated by Django 5.0.1 on 2024-05-24 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0103_alter_incident_client"),
        ("employees", "0060_alter_progressreport_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="incident",
            name="involved_children",
            field=models.ManyToManyField(related_name="incidents_list", to="client.clientdetails"),
        ),
    ]

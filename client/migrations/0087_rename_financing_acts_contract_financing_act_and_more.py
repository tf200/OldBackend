# Generated by Django 5.0.1 on 2024-04-29 14:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0086_alter_careplan_client_clientcurrentlevel"),
    ]

    operations = [
        migrations.RenameField(
            model_name="contract",
            old_name="financing_acts",
            new_name="financing_act",
        ),
        migrations.RenameField(
            model_name="contract",
            old_name="financing_options",
            new_name="financing_option",
        ),
    ]

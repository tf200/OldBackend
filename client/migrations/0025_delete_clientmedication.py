# Generated by Django 5.0.1 on 2024-03-04 09:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0024_alter_clientdetails_status"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ClientMedication",
        ),
    ]

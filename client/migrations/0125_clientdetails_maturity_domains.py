# Generated by Django 5.0.1 on 2024-07-01 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0124_alter_sender_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="clientdetails",
            name="maturity_domains",
            field=models.JSONField(blank=True, default=list),
        ),
    ]

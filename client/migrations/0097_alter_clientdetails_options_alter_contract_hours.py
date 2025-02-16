# Generated by Django 5.0.1 on 2024-05-15 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0096_clientdetails_gps_position_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="clientdetails",
            options={"ordering": ("-id",), "verbose_name": "Client"},
        ),
        migrations.AlterField(
            model_name="contract",
            name="hours",
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]

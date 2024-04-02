# Generated by Django 5.0.1 on 2024-02-09 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0020_emotionalstate_physicalstate"),
    ]

    operations = [
        migrations.AddField(
            model_name="clientdetails",
            name="identity",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="clientdetails",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("In Care", "In Care"),
                    ("On Waiting List", "On Waiting List"),
                    ("Out Of Concern", "Out Of Concern"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]

# Generated by Django 5.0.1 on 2024-02-09 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0022_clientagreement_created_clientallergy_created_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="physicalstate",
            name="client",
        ),
        migrations.AddField(
            model_name="clientdetails",
            name="birthplace",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="clientdetails",
            name="bsn",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="clientdetails",
            name="source",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.DeleteModel(
            name="EmotionalState",
        ),
        migrations.DeleteModel(
            name="PhysicalState",
        ),
    ]

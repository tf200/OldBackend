# Generated by Django 5.0.1 on 2024-04-06 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessments", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assessment",
            name="content",
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]

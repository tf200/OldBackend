# Generated by Django 5.0.1 on 2024-05-20 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0058_alter_progressreport_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="progressreport",
            name="emotional_state",
            field=models.CharField(
                choices=[
                    ("normal", "Normal"),
                    ("excited", "Excited"),
                    ("happy", "Happy"),
                    ("sad", "Sad"),
                    ("angry", "Angry"),
                    ("anxious", "Anxious"),
                    ("depressed", "Depressed"),
                ],
                default="normal",
            ),
        ),
    ]

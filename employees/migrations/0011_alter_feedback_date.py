# Generated by Django 5.0.1 on 2024-02-08 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0010_feedback_author"),
    ]

    operations = [
        migrations.AlterField(
            model_name="feedback",
            name="date",
            field=models.DateField(auto_now_add=True),
        ),
    ]

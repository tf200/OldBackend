# Generated by Django 5.0.1 on 2024-02-15 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("adminmodif", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="groupmembership",
            name="end_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="groupmembership",
            name="start_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]

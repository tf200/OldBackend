# Generated by Django 5.0.1 on 2024-03-18 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0028_employeeprofile_location"),
    ]

    operations = [
        migrations.AddField(
            model_name="employeeprofile",
            name="has_borrowed",
            field=models.BooleanField(default=False),
        ),
    ]

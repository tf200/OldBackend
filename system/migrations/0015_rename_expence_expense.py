# Generated by Django 5.0.1 on 2024-04-27 15:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("system", "0014_expence"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Expence",
            new_name="Expense",
        ),
    ]

# Generated by Django 5.0.1 on 2024-04-26 11:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0074_careplangoals_careplanobjectives"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="CarePlanGoals",
            new_name="CarePlanGoal",
        ),
        migrations.RenameModel(
            old_name="CarePlanObjectives",
            new_name="CarePlanObjective",
        ),
    ]

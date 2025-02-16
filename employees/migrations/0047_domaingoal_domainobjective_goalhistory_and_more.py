# Generated by Django 5.0.1 on 2024-05-01 15:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessments", "0003_alter_assessment_domain"),
        ("client", "0091_remove_domainobjective_goal_remove_goalhistory_goal_and_more"),
        ("employees", "0046_progressreport_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="DomainGoal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("desc", models.TextField(blank=True, default="", null=True)),
                ("is_approved", models.BooleanField(default=False)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="goals",
                        to="client.clientdetails",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="goals",
                        to="employees.employeeprofile",
                    ),
                ),
                (
                    "domain",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="goals",
                        to="assessments.assessmentdomain",
                    ),
                ),
                (
                    "reviewed_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reviewed_goals",
                        to="employees.employeeprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DomainObjective",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("desc", models.TextField(blank=True, default="", null=True)),
                ("rating", models.FloatField(default=0)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="objectives",
                        to="client.clientdetails",
                    ),
                ),
                (
                    "goal",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="objectives",
                        to="employees.domaingoal",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="GoalHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("rating", models.FloatField(default=0)),
                ("date", models.DateField(auto_now_add=True, db_index=True)),
                (
                    "goal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="history",
                        to="employees.domaingoal",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ObjectiveHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("rating", models.FloatField(default=0)),
                ("date", models.DateField(auto_now_add=True, db_index=True)),
                (
                    "objective",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="history",
                        to="employees.domainobjective",
                    ),
                ),
            ],
        ),
    ]

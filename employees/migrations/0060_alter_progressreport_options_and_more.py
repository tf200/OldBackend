# Generated by Django 5.0.1 on 2024-05-22 13:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0059_alter_progressreport_emotional_state"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="progressreport",
            options={"ordering": ("-created",)},
        ),
        migrations.AlterField(
            model_name="clientmedication",
            name="administered_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="medications_administered",
                to="employees.employeeprofile",
            ),
        ),
    ]

# Generated by Django 5.0.1 on 2024-05-31 09:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0115_youthcareintake_alter_consentdeclaration_options"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="youthcareintake",
            name="financing_form",
        ),
        migrations.AddField(
            model_name="youthcareintake",
            name="client",
            field=models.ForeignKey(
                default=11,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="youth_care_intakes",
                to="client.clientdetails",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="youthcareintake",
            name="financing_acts",
            field=models.CharField(
                choices=[
                    ("WMO", "WMO"),
                    ("ZVW", "ZVW"),
                    ("WLZ", "WLZ"),
                    ("JW", "JW"),
                    ("WPG", "WPG"),
                ],
                default=21,
                max_length=20,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="youthcareintake",
            name="financing_options",
            field=models.CharField(
                choices=[("ZIN", "ZIN"), ("PGB", "PGB")], default="PGB", max_length=20
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="youthcareintake",
            name="gender",
            field=models.CharField(max_length=30),
        ),
    ]

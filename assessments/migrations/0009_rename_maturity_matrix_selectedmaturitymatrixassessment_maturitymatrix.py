# Generated by Django 5.0.1 on 2024-07-04 17:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("assessments", "0008_alter_maturitymatrix_client"),
    ]

    operations = [
        migrations.RenameField(
            model_name="selectedmaturitymatrixassessment",
            old_name="maturity_matrix",
            new_name="maturitymatrix",
        ),
    ]

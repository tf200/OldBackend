# Generated by Django 5.0.1 on 2024-05-01 16:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("system", "0016_expense_attachments_ids"),
    ]

    operations = [
        migrations.RenameField(
            model_name="expense",
            old_name="attachments_ids",
            new_name="attachment_ids",
        ),
    ]

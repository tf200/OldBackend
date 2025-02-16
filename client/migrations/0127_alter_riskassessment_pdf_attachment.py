# Generated by Django 5.0.1 on 2024-07-10 18:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0126_collaborationagreement_pdf_attachment_and_more'),
        ('system', '0024_alter_protectedemail_email_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='riskassessment',
            name='pdf_attachment',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='system.attachmentfile'),
        ),
    ]

# Generated by Django 5.0.1 on 2024-01-29 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0002_remove_clientdetails_user_clientdetails_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientdetails',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]

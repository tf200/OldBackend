# Generated by Django 5.0.1 on 2024-03-15 11:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_location'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='adress',
            new_name='address',
        ),
    ]

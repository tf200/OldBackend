# Generated by Django 5.0.1 on 2024-03-26 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_rename_adress_location_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='capacity',
            field=models.IntegerField(null=True),
        ),
    ]

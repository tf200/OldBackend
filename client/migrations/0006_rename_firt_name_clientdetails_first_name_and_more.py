# Generated by Django 5.0.1 on 2024-02-01 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0005_alter_clientdetails_filenumber_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clientdetails',
            old_name='firt_name',
            new_name='first_name',
        ),
        migrations.RenameField(
            model_name='clientemergencycontact',
            old_name='adress',
            new_name='address',
        ),
        migrations.AddField(
            model_name='clientdetails',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='clients_pics/'),
        ),
    ]

# Generated by Django 5.0.1 on 2024-02-20 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0024_alter_clientdetails_status'),
        ('planning', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='clients',
            field=models.ManyToManyField(blank=True, related_name='client_appointments', to='client.clientdetails'),
        ),
    ]

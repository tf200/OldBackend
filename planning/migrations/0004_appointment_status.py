# Generated by Django 5.0.1 on 2024-02-21 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0003_temporaryfile'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]

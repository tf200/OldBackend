# Generated by Django 5.0.1 on 2024-02-29 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0019_remove_employeeprofile_graduation_year_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progressreport',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

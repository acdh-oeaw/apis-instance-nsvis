# Generated by Django 5.1.7 on 2025-06-16 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_instance_nsvis', '0054_institution_details_versioninstitution_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='collaborateswith',
            name='details',
            field=models.TextField(blank=True, null=True, verbose_name='details'),
        ),
    ]

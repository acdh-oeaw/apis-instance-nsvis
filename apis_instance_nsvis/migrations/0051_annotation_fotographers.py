# Generated by Django 5.1.7 on 2025-05-23 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_instance_nsvis', '0050_alter_institution_options_alter_institution_label_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotation',
            name='fotographers',
            field=models.JSONField(editable=False, null=True),
        ),
    ]

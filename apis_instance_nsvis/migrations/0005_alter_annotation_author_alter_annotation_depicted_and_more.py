# Generated by Django 5.1.2 on 2024-11-28 10:59

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_instance_nsvis', '0004_annotation_author_annotation_caption_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='author',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(), null=True, size=None),
        ),
        migrations.AlterField(
            model_name='annotation',
            name='depicted',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(), null=True, size=None),
        ),
        migrations.AlterField(
            model_name='annotation',
            name='topic',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(), null=True, size=None),
        ),
    ]
# Generated by Django 5.1.2 on 2025-01-08 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_instance_nsvis', '0005_alter_annotation_author_alter_annotation_depicted_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotation',
            name='internal_comment',
            field=models.TextField(blank=True, null=True),
        ),
    ]
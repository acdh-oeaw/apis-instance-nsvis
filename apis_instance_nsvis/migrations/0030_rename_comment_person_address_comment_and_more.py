# Generated by Django 5.1.2 on 2025-02-25 09:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apis_instance_nsvis', '0029_alter_person_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='person',
            old_name='comment',
            new_name='address_comment',
        ),
        migrations.RenameField(
            model_name='versionperson',
            old_name='comment',
            new_name='address_comment',
        ),
    ]

# Generated by Django 5.1.2 on 2024-11-13 08:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_instance_nsvis', '0001_initial'),
        ('relations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IsLearningAt',
            fields=[
                ('relation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='relations.relation')),
            ],
            bases=('relations.relation',),
        ),
    ]

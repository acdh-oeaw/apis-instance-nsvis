# Generated by Django 5.1.7 on 2025-04-04 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_instance_nsvis', '0040_remove_versionaddressdata_history_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bornin',
            name='date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='bornin',
            name='date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='bornin',
            name='date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='collaborateswith',
            name='from_date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='collaborateswith',
            name='from_date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='collaborateswith',
            name='from_date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='collaborateswith',
            name='to_date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='collaborateswith',
            name='to_date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='collaborateswith',
            name='to_date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='diedin',
            name='date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='diedin',
            name='date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='diedin',
            name='date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='exilein',
            name='from_date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='exilein',
            name='from_date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='exilein',
            name='from_date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='exilein',
            name='to_date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='exilein',
            name='to_date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='exilein',
            name='to_date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='hasstudioin',
            name='from_date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='hasstudioin',
            name='from_date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='hasstudioin',
            name='from_date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='hasstudioin',
            name='to_date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='hasstudioin',
            name='to_date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='hasstudioin',
            name='to_date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='imprisonedin',
            name='from_date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='imprisonedin',
            name='from_date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='imprisonedin',
            name='from_date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='imprisonedin',
            name='to_date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='imprisonedin',
            name='to_date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='imprisonedin',
            name='to_date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='islearningat',
            name='from_date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='islearningat',
            name='from_date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='islearningat',
            name='from_date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='islearningat',
            name='to_date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='islearningat',
            name='to_date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='islearningat',
            name='to_date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='ismemberof',
            name='from_date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='ismemberof',
            name='from_date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='ismemberof',
            name='from_date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='ismemberof',
            name='to_date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='ismemberof',
            name='to_date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='ismemberof',
            name='to_date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='livesin',
            name='from_date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='livesin',
            name='from_date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='livesin',
            name='from_date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='livesin',
            name='to_date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='livesin',
            name='to_date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='livesin',
            name='to_date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='feature_code',
            field=models.CharField(blank=True, default='', help_text='<a href="https://www.geonames.org/export/codes.html">Geonames Feature Code List</a>', max_length=16, verbose_name='feature code'),
        ),
        migrations.AlterField(
            model_name='place',
            name='label',
            field=models.CharField(blank=True, default='', max_length=4096, verbose_name='label'),
        ),
        migrations.AlterField(
            model_name='place',
            name='latitude',
            field=models.FloatField(blank=True, null=True, verbose_name='latitude'),
        ),
        migrations.AlterField(
            model_name='place',
            name='longitude',
            field=models.FloatField(blank=True, null=True, verbose_name='longitude'),
        ),
        migrations.AlterField(
            model_name='versionplace',
            name='feature_code',
            field=models.CharField(blank=True, default='', help_text='<a href="https://www.geonames.org/export/codes.html">Geonames Feature Code List</a>', max_length=16, verbose_name='feature code'),
        ),
        migrations.AlterField(
            model_name='versionplace',
            name='label',
            field=models.CharField(blank=True, default='', max_length=4096, verbose_name='label'),
        ),
        migrations.AlterField(
            model_name='versionplace',
            name='latitude',
            field=models.FloatField(blank=True, null=True, verbose_name='latitude'),
        ),
        migrations.AlterField(
            model_name='versionplace',
            name='longitude',
            field=models.FloatField(blank=True, null=True, verbose_name='longitude'),
        ),
        migrations.AlterField(
            model_name='worksas',
            name='from_date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='worksas',
            name='from_date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='worksas',
            name='from_date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='worksas',
            name='to_date_date_from',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='worksas',
            name='to_date_date_sort',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='worksas',
            name='to_date_date_to',
            field=models.DateField(auto_created=True, blank=True, editable=False, null=True),
        ),
    ]

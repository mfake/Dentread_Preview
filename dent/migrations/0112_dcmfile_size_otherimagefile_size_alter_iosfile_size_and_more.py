# Generated by Django 4.0.4 on 2022-09-01 13:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0111_iosfile_size_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dcmfile',
            name='size',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='otherimagefile',
            name='size',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='iosfile',
            name='size',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 1, 18, 39, 0, 266190)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 1, 18, 39, 0, 286075)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 1, 18, 39, 0, 286075)),
        ),
    ]

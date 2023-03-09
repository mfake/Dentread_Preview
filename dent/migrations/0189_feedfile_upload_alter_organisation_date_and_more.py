# Generated by Django 4.1 on 2022-10-08 10:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0188_feedfile_filecomment_feedfile_filestatus_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedfile',
            name='upload',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 8, 16, 19, 52, 51907)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 8, 16, 19, 52, 84974)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 8, 16, 19, 52, 85968)),
        ),
    ]

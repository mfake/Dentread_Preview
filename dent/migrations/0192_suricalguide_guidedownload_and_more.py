# Generated by Django 4.1 on 2022-10-08 14:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0191_suricalguide_guideupload_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='suricalguide',
            name='GuideDownload',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='suricalguide',
            name='GuideUploadDate',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 8, 19, 41, 0, 785920)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 8, 19, 41, 0, 822832)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 8, 19, 41, 0, 823832)),
        ),
    ]
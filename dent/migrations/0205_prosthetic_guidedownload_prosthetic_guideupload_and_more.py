# Generated by Django 4.1 on 2022-10-18 05:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0204_alter_organisation_date_alter_pack_rdate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='prosthetic',
            name='GuideDownload',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='GuideUpload',
            field=models.CharField(blank=True, max_length=800, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='GuideUploadDate',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 18, 11, 5, 3, 973529)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 18, 11, 5, 4, 78540)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 18, 11, 5, 4, 80538)),
        ),
    ]

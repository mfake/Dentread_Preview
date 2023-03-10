# Generated by Django 4.0.4 on 2022-10-19 11:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0209_iosfile_site_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='prosthetic',
            name='fileStatus',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 19, 16, 39, 48, 526710)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 19, 16, 39, 48, 628895)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 19, 16, 39, 48, 628895)),
        ),
    ]

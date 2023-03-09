# Generated by Django 4.0.4 on 2022-10-21 14:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0215_notification_sent_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='iosfile',
            name='download',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='iosfile',
            name='re_upload',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 21, 19, 46, 24, 409947)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 21, 19, 46, 24, 494865)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 21, 19, 46, 24, 495912)),
        ),
    ]

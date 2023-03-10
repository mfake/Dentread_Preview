# Generated by Django 4.0.4 on 2022-12-21 13:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0254_prosthetic_designcomment_prosthetic_designstatus_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='prosthetic',
            name='paymentStatus',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='serviceorder',
            name='referTo',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 21, 19, 1, 11, 39598)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 21, 19, 1, 11, 269917)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 21, 19, 1, 11, 269917)),
        ),
    ]

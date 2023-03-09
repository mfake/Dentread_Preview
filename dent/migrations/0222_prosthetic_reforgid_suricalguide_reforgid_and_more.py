# Generated by Django 4.0.4 on 2022-11-02 07:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0221_prosthetic_designcheck_prosthetic_pickupaddress_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='prosthetic',
            name='reforgid',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='suricalguide',
            name='reforgid',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 2, 13, 14, 58, 332154)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 2, 13, 14, 58, 399930)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 2, 13, 14, 58, 399930)),
        ),
    ]

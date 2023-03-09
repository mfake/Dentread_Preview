# Generated by Django 4.0.4 on 2022-11-11 15:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0231_prosthetic_fabricationcomplete_prosthetic_prevstatus_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='suricalguide',
            name='fabricationComplete',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 11, 20, 40, 2, 862279)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 11, 20, 40, 2, 969441)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 11, 20, 40, 2, 969441)),
        ),
    ]
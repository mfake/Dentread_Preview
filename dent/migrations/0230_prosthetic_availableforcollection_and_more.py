# Generated by Django 4.0.4 on 2022-11-06 05:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0229_prosthetic_orderpickup_prosthetic_orderpickuptime_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='prosthetic',
            name='availableForCollection',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='dataApprove',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='dataApproveComment',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 6, 11, 18, 57, 70566)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 6, 11, 18, 57, 101826)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 6, 11, 18, 57, 101826)),
        ),
    ]
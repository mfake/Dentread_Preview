# Generated by Django 4.0.4 on 2022-09-19 11:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0168_imageanalysis_mailstatus_imageanalysis_shipped_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicelog',
            name='patient',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 19, 16, 41, 13, 271284)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 19, 16, 41, 13, 287144)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 19, 16, 41, 13, 287144)),
        ),
    ]

# Generated by Django 4.1 on 2022-10-08 12:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0190_feedfile_date_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='suricalguide',
            name='GuideUpload',
            field=models.CharField(blank=True, max_length=800, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 8, 17, 39, 59, 648209)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 8, 17, 39, 59, 681404)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 8, 17, 39, 59, 682399)),
        ),
    ]

# Generated by Django 4.0.4 on 2022-11-04 09:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0227_serviceorder_preferreddata_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='prosthetic',
            name='cancellationDateTime',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='cancellationReason',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 4, 15, 14, 32, 813085)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 4, 15, 14, 32, 858082)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 4, 15, 14, 32, 858082)),
        ),
    ]

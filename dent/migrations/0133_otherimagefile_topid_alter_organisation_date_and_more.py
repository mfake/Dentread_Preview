# Generated by Django 4.0.4 on 2022-09-06 12:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0132_radiologycalservices_parentpatient_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='otherimagefile',
            name='topid',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 6, 18, 27, 20, 807276)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 6, 18, 27, 20, 827282)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 6, 18, 27, 20, 827282)),
        ),
    ]

# Generated by Django 4.0.4 on 2022-09-14 09:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0147_radiologycalservices_refer_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='radiologycalservices',
            name='mailstatus',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='radiologycalservices',
            name='pt_contact',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='radiologycalservices',
            name='pt_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 14, 15, 23, 12, 564678)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 14, 15, 23, 12, 595941)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 14, 15, 23, 12, 595941)),
        ),
    ]

# Generated by Django 4.0.4 on 2022-09-09 12:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0135_radiologycalservices_item_id_serviceorder_order_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceorder',
            name='shipped_by',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='serviceorder',
            name='tracking_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 9, 18, 10, 13, 505939)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 9, 18, 10, 13, 518040)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 9, 18, 10, 13, 518040)),
        ),
    ]

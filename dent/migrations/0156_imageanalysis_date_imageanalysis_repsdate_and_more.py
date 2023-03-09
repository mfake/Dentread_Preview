# Generated by Django 4.0.4 on 2022-09-17 08:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0155_alter_organisation_date_alter_pack_rdate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageanalysis',
            name='date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='imageanalysis',
            name='repsdate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 17, 14, 25, 10, 957197)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 17, 14, 25, 10, 987200)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 17, 14, 25, 10, 987200)),
        ),
    ]

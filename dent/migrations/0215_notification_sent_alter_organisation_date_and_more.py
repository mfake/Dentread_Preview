# Generated by Django 4.0.4 on 2022-10-21 07:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0214_notification_date_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 21, 12, 36, 16, 524977)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 21, 12, 36, 16, 604777)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 21, 12, 36, 16, 604777)),
        ),
    ]
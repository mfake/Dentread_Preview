# Generated by Django 4.0.4 on 2022-11-18 17:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0235_alter_organisation_date_alter_pack_rdate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='prosthetic',
            name='application',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='item',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='submethod',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='warranty',
            field=models.IntegerField(default=5),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 18, 22, 38, 42, 425401)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 18, 22, 38, 42, 496565)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 18, 22, 38, 42, 496565)),
        ),
    ]
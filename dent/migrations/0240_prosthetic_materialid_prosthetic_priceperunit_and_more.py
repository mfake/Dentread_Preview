# Generated by Django 4.0.4 on 2022-11-26 07:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0239_rename_finding_equires_radiologycalservices_finding_requires_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='prosthetic',
            name='materialId',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='pricePerUnit',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='shade',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='shadeType',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='unit',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='laborderitem',
            name='warranty',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 26, 12, 54, 16, 357555)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 26, 12, 54, 16, 401837)),
        ),
        migrations.AlterField(
            model_name='prosthetic',
            name='warranty',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 26, 12, 54, 16, 401837)),
        ),
    ]

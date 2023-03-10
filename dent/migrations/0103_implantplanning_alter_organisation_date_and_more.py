# Generated by Django 4.0.4 on 2022-08-16 09:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0102_alter_imageanalysis_price_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImplantPlanning',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('repid', models.IntegerField(blank=True, null=True)),
                ('tooth', models.CharField(blank=True, max_length=200, null=True)),
                ('data_type', models.CharField(blank=True, max_length=200, null=True)),
                ('service_catagory', models.CharField(blank=True, max_length=200, null=True)),
                ('planning_type', models.CharField(blank=True, max_length=200, null=True)),
                ('price', models.IntegerField(blank=True, null=True)),
                ('remark', models.CharField(blank=True, max_length=800, null=True)),
                ('status', models.CharField(blank=True, max_length=800, null=True)),
                ('comment', models.CharField(blank=True, max_length=800, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 16, 14, 44, 38, 565083)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 16, 14, 44, 38, 580693)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 16, 14, 44, 38, 580693)),
        ),
    ]

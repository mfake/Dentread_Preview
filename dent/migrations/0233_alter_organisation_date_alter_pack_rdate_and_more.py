# Generated by Django 4.0.4 on 2022-11-12 05:26

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0232_suricalguide_fabricationcomplete_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 12, 10, 56, 38, 587214)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 12, 10, 56, 38, 632217)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 12, 10, 56, 38, 632217)),
        ),
        migrations.CreateModel(
            name='LabOrderItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(blank=True, max_length=200, null=True)),
                ('method', models.CharField(blank=True, max_length=200, null=True)),
                ('material', models.CharField(blank=True, max_length=200, null=True)),
                ('application', models.CharField(blank=True, max_length=200, null=True)),
                ('warrenty', models.IntegerField()),
                ('price', models.IntegerField()),
                ('orgid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dent.organisation')),
            ],
        ),
    ]

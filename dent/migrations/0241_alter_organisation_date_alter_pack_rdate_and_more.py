# Generated by Django 4.0.4 on 2022-11-26 07:32

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0240_prosthetic_materialid_prosthetic_priceperunit_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 26, 13, 2, 29, 171216)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 26, 13, 2, 29, 218090)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 26, 13, 2, 29, 218090)),
        ),
        migrations.CreateModel(
            name='Shade',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('topcat', models.CharField(blank=True, max_length=100, null=True)),
                ('shadeType', models.CharField(blank=True, max_length=100, null=True)),
                ('shade', models.CharField(blank=True, max_length=100, null=True)),
                ('orgid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dent.organisation')),
            ],
        ),
    ]

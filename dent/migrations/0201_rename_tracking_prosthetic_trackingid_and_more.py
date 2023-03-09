# Generated by Django 4.0.4 on 2022-10-12 12:19

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0200_suricalguide_orderdelivercomment_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='prosthetic',
            old_name='tracking',
            new_name='trackingId',
        ),
        migrations.RemoveField(
            model_name='prosthetic',
            name='casetype',
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='DispatchAddress',
            field=models.CharField(blank=True, max_length=800, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='DispatchComment',
            field=models.CharField(blank=True, max_length=800, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='DispatchDate',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='badge',
            field=models.CharField(default=1, max_length=400),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='designUploadDate',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='expectedDate',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='item_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='orderDeliverComment',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='orderDeliverConfirmationC',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='orderDeliverConfirmationL',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='orderDeliverDate',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='orgid',
            field=models.ForeignKey(default=38, on_delete=django.db.models.deletion.CASCADE, to='dent.organisation'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='parent_orgid',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='pid',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='service_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='shipped_by',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='prosthetic',
            name='sodrid',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 12, 17, 48, 10, 755694)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 12, 17, 48, 10, 786952)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 12, 17, 48, 10, 786952)),
        ),
    ]

# Generated by Django 4.0.4 on 2022-10-20 14:01

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0211_iosfile_badge_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 20, 19, 31, 56, 200709)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 20, 19, 31, 56, 264624)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 20, 19, 31, 56, 265624)),
        ),
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('parent_orgid', models.CharField(blank=True, max_length=200, null=True)),
                ('repid', models.IntegerField(blank=True, null=True)),
                ('serviceOrderId', models.CharField(blank=True, max_length=150, null=True)),
                ('lineItemId', models.CharField(blank=True, max_length=150, null=True)),
                ('sentTo', models.IntegerField(blank=True, null=True)),
                ('user', models.CharField(blank=True, max_length=50, null=True)),
                ('usertype', models.CharField(max_length=200)),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('event', models.CharField(blank=True, max_length=200, null=True)),
                ('details', models.CharField(blank=True, max_length=200, null=True)),
                ('hyperLink', models.CharField(blank=True, max_length=200, null=True)),
                ('read', models.BooleanField(default=False)),
                ('orgid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dent.organisation')),
            ],
        ),
    ]
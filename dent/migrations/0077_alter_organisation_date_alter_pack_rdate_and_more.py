# Generated by Django 4.0.3 on 2022-07-10 08:02

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0076_users_edu_users_spec_alter_organisation_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 10, 13, 32, 10, 243052)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 10, 13, 32, 10, 252008)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 10, 13, 32, 10, 252008)),
        ),
        migrations.CreateModel(
            name='Tempid',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('repid', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(max_length=200)),
                ('orgid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dent.organisation')),
            ],
        ),
    ]
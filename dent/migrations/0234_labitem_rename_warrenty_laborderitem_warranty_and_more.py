# Generated by Django 4.0.4 on 2022-11-15 07:05

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0233_alter_organisation_date_alter_pack_rdate_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LabItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('item', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.RenameField(
            model_name='laborderitem',
            old_name='warrenty',
            new_name='warranty',
        ),
        migrations.AddField(
            model_name='laborderitem',
            name='details',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
        migrations.AddField(
            model_name='laborderitem',
            name='item',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='laborderitem',
            name='submethod',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 15, 12, 34, 18, 368045)),
        ),
        migrations.AlterField(
            model_name='pack',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 15, 12, 34, 18, 453129)),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='rdate',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 15, 12, 34, 18, 453129)),
        ),
        migrations.CreateModel(
            name='LabMaterial',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('material', models.CharField(blank=True, max_length=100, null=True)),
                ('itemId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dent.labitem')),
                ('orgid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dent.organisation')),
            ],
        ),
        migrations.CreateModel(
            name='AddOnLabServices',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('addOnService', models.CharField(blank=True, max_length=100, null=True)),
                ('price', models.IntegerField()),
                ('materialId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dent.labmaterial')),
                ('orgid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dent.organisation')),
            ],
        ),
        migrations.AddField(
            model_name='laborderitem',
            name='itemId',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='dent.labitem'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='laborderitem',
            name='materialId',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='dent.labmaterial'),
            preserve_default=False,
        ),
    ]
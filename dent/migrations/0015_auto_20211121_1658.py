# Generated by Django 3.1.6 on 2021-11-21 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0014_auto_20211104_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='expenses',
            name='saleamount',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expenses',
            name='amount',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

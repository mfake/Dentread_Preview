# Generated by Django 3.1.6 on 2021-11-03 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0008_auto_20211029_2150'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='mailstatus',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]

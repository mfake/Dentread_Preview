# Generated by Django 3.1.6 on 2021-12-26 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0018_auto_20211224_2012'),
    ]

    operations = [
        migrations.AddField(
            model_name='refpt',
            name='ref_centre',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]

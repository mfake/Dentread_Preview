# Generated by Django 3.1.6 on 2021-10-28 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0005_auto_20211024_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='refdoctor',
            name='clcontact',
            field=models.EmailField(max_length=254),
        ),
    ]

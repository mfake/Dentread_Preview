# Generated by Django 4.0.3 on 2022-04-13 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0026_department_remove_users_organisation_users_orgid'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='propic',
            field=models.ImageField(default=1, upload_to='static/profilepic/'),
            preserve_default=False,
        ),
    ]

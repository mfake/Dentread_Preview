# Generated by Django 3.1.6 on 2021-11-04 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dent', '0012_appointment_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sign',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sid', models.IntegerField(blank=True, null=True)),
                ('sign', models.ImageField(upload_to='static/signs/')),
            ],
        ),
    ]
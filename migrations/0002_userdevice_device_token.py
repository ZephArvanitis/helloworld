# Generated by Django 3.1.7 on 2021-04-03 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helloworld', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdevice',
            name='device_token',
            field=models.CharField(default='ABCDEFGH', max_length=100),
            preserve_default=False,
        ),
    ]

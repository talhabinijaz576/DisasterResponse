# Generated by Django 3.1.5 on 2021-02-24 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control_room', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='road',
            name='oneway',
            field=models.BooleanField(),
        ),
    ]

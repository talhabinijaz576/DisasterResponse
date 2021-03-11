# Generated by Django 3.1.5 on 2021-02-24 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control_room', '0002_auto_20210224_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='road',
            name='lanes',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='road',
            name='length',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='road',
            name='maxspeed',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='road',
            name='oneway',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='shape',
            name='latitude',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='shape',
            name='longitude',
            field=models.FloatField(),
        ),
    ]
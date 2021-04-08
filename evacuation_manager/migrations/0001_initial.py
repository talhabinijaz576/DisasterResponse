# Generated by Django 3.1.5 on 2021-04-08 14:23

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Evacuation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='', max_length=50)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_ended', models.DateTimeField(blank=True, null=True)),
                ('size', models.IntegerField()),
                ('actions', models.CharField(default='', max_length=100)),
                ('is_running', models.BooleanField(default=True)),
            ],
        ),
    ]

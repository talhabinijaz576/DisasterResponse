# Generated by Django 3.1.5 on 2021-04-15 12:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('evacuation_manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DisasterEvent',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='', max_length=50)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_ended', models.DateTimeField(blank=True, null=True)),
                ('size', models.IntegerField()),
                ('events', models.CharField(default='', max_length=100)),
                ('is_running', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='EvacuationEvent',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='', max_length=50)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_ended', models.DateTimeField(blank=True, null=True)),
                ('size', models.IntegerField()),
                ('events', models.CharField(default='', max_length=100)),
                ('is_running', models.BooleanField(default=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Evacuation',
        ),
    ]
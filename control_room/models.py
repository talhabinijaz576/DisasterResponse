from django.db import models
from django.dispatch import receiver
from foo_auth.models import User
from django.utils import timezone
from django.conf import settings



class Hospital(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(unique = False, max_length = 50, default='')
    date_modified = models.DateTimeField(default=timezone.now)
    latitude = models.FloatField()
    longitude = models.FloatField()
    capacity = models.IntegerField()
    vehicles_available = models.IntegerField()

class FireStation(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(unique = False, max_length = 50, default='')
    date_modified = models.DateTimeField(default=timezone.now)
    latitude = models.FloatField()
    longitude = models.FloatField()
    capacity = models.IntegerField()
    vehicles_available = models.IntegerField()

class PoliceStation(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(unique = False, max_length = 50, default='')
    date_modified = models.DateTimeField(default=timezone.now)
    latitude = models.FloatField()
    longitude = models.FloatField()
    capacity = models.IntegerField()
    vehicles_available = models.IntegerField()


class EvacuationPoint(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(unique = False, max_length = 50, default='')
    date_modified = models.DateTimeField(default=timezone.now)
    latitude = models.FloatField()
    longitude = models.FloatField()
    capacity = models.IntegerField()
    vehicles_available = models.IntegerField()


class Road(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(unique = False, max_length = 50, default='')
    lanes = models.IntegerField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    maxspeed = models.FloatField(blank=True, null=True)
    oneway = models.BooleanField(blank=True, null=True)


class Shape(models.Model):

    id = models.AutoField(primary_key=True)
    shape_id = models.CharField(max_length = 50, default="")
    latitude = models.FloatField()
    longitude = models.FloatField()
    #models.ForeignKey(User, on_delete=models.CASCADE, default='')

class Disaster(models.Model):

    id = models.AutoField(primary_key=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    intensity = models.FloatField()
    type = models.CharField(unique = False, max_length = 50, default='')
    stAddress = models.CharField(unique = False, max_length = 50, default='')
    additionalInfo = models.CharField(unique = False, max_length = 50, default='')
    casualities = models.IntegerField()
    isActive = models.BooleanField(blank=True, null=True)

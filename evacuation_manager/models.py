from django.db import models
from django.dispatch import receiver
from foo_auth.models import User
from django.utils import timezone
from django.conf import settings
import os



class EvacuationEvent(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length = 50, default='')
    latitude = models.FloatField()
    longitude = models.FloatField()
    date_created = models.DateTimeField(default=timezone.now)
    date_ended = models.DateTimeField(blank=True, null=True)
    size = models.IntegerField()
    events = models.CharField(max_length = 100, default='')
    is_running = models.BooleanField(default=True)

    def image(self):
        image_path = os.path.join(settings.BASE_DIR, "FILES", "evacuation_"+str(self.id)+".png")
        return image_path

    def end(self):
        self.is_running = False
        self.date_ended = timezone.now()



class DisasterEvent(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length = 50, default='')
    latitude = models.FloatField()
    longitude = models.FloatField()
    date_created = models.DateTimeField(default=timezone.now)
    date_ended = models.DateTimeField(blank=True, null=True)
    size = models.IntegerField()
    events = models.CharField(max_length = 100, default='')
    is_running = models.BooleanField(default=True)

    def image(self):
        image_path = os.path.join(settings.BASE_DIR, "FILES", "disaster_"+str(self.id)+".png")
        return image_path


    def end(self):
        self.is_running = False
        self.date_ended = timezone.now()


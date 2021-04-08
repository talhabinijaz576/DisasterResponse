from django.db import models
from django.dispatch import receiver
from foo_auth.models import User
from django.utils import timezone
from django.conf import settings



class Evacuation(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length = 50, default='')
    latitude = models.FloatField()
    longitude = models.FloatField()
    date_created = models.DateTimeField(default=timezone.now)
    date_ended = models.DateTimeField(blank=True, null=True)
    size = models.IntegerField()
    actions = models.CharField(max_length = 100, default='')
    is_running = models.BooleanField(default=True)

    def image(self):
        image_path = os.path.join(settings.evacuation_files, str(self.id)+".png")

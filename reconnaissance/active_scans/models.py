from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
#from events.models import Event
#from assets.models import Asset, AssetGroup
#from engines.models import Engine, EnginePolicy, EngineInstance

from django_celery_beat.models import PeriodicTask
import uuid, datetime, os

SCAN_STATUS = ('created', 'started', 'done', 'error', 'trashed')

PERIOD_CHOICES = (
    ('days', 'Days'),
    ('hours', 'Hours'),
    ('minutes', 'Minutes'),
    ('seconds', 'Seconds'),
    #('microseconds', 'Microseconds'),
)

SCAN_TYPES = (
    ('single', 'single'),
    ('periodic', 'periodic'),
    ('scheduled', 'scheduled'),
)

class Nmap(models.Model):
	IP = models.CharField(max_length=1200)
	FQDN = models.CharField(max_length=1200)
	PORT = models.CharField(max_length=1200)
	PROTOCOL = models.CharField(max_length=1200)
	SERVICE = models.CharField(max_length=1200)
	VERSION = models.CharField(max_length=1200)

	class Meta:
		unique_together = (("IP","PORT"))
from django.db import models
from django.contrib.auth.models import User

class Visitor(models.Model):
    session_key = models.CharField(max_length=40, primary_key=True)
    ip_address = models.CharField(max_length=20)
    user = models.ForeignKey(User, null=True)
    user_agent = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    last_update = models.DateTimeField()

    class Meta:
        unique_together = ['session_key', 'ip_address']

class BannedIP(models.Model):
    ip_address = models.IPAddressField()

    def __unicode__(self):
        return self.ip_address

    class Meta:
        ordering = ['ip_address']
        verbose_name = 'Banned IP'
        verbose_name_plural = 'Banned IPs'
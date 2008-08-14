from django.db import models
from django.contrib.auth.models import User
from tracking import utils
from datetime import datetime, timedelta

class VisitorManager(models.Manager):
    def active(self, timeout=None):
        if not timeout:
            timeout = utils.get_timeout()

        now = datetime.now()
        cutoff = now - timedelta(minutes=timeout)
        
        return self.get_query_set().filter(last_update__gte=cutoff)

class Visitor(models.Model):
    session_key = models.CharField(max_length=40)
    ip_address = models.CharField(max_length=20)
    user = models.ForeignKey(User, null=True)
    user_agent = models.CharField(max_length=255)
    referrer = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    page_views = models.PositiveIntegerField(default=0)
    last_update = models.DateTimeField()

    objects = VisitorManager()

    class Meta:
        ordering = ['-last_update']
        unique_together = ['session_key', 'ip_address']

class UntrackedUserAgent(models.Model):
    keyword = models.CharField(max_length=100, help_text='Part or all of a user-agent string.  For example, "Googlebot" here will be found in "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" and that visitor will not be tracked.')

    def __unicode__(self):
        return self.keyword

    class Meta:
        ordering = ['keyword']
        verbose_name = 'Untracked User-Agent'
        verbose_name_plural = 'Untracked User-Agents'

class BannedIP(models.Model):
    ip_address = models.IPAddressField('IP Address', help_text='The IP address that should be banned')

    def __unicode__(self):
        return self.ip_address

    class Meta:
        ordering = ['ip_address']
        verbose_name = 'Banned IP'
        verbose_name_plural = 'Banned IPs'
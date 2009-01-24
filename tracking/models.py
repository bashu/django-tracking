from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from tracking import utils
from datetime import datetime, timedelta
import os

try:
    import GeoIP
except ImportError:
    GeoIP = None

class VisitorManager(models.Manager):
    def active(self, timeout=None):
        """
        Retrieves only visitors who have been active within the timeout
        period.
        """
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
    session_start = models.DateTimeField()
    last_update = models.DateTimeField()

    objects = VisitorManager()

    def _time_on_site(self):
        """
        Attempts to determine the amount of time a visitor has spent on the
        site based upon their information that's in the database.
        """
        if self.session_start:
            seconds = (self.last_update - self.session_start).seconds

            hours = seconds / 3600
            seconds -= hours * 3600
            minutes = seconds / 60
            seconds -= minutes * 60

            return u'%i:%02i:%02i' % (hours, minutes, seconds)
        else:
            return u'unknown'
    time_on_site = property(_time_on_site)

    def _get_geoip_data(self):
        """
        Attempts to retrieve MaxMind GeoIP data based upon the visitor's IP
        """
        if getattr(settings, 'TRACKING_USE_GEOIP', False) and GeoIP:
            geoip_data_file = getattr(settings, 'GEOIP_DATA_FILE', None)

            if geoip_data_file:
                assert os.access(geoip_data_file, os.R_OK)
                gip = GeoIP.open(geoip_data_file, GeoIP.GEOIP_MEMORY_CACHE)
            else:
                gip = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)

            try:
                return gip.record_by_addr(self.ip_address)
            except SystemError:
                # if we get here, chances are that we didn't get a result for
                # the IP
                pass
        return None
    geoip_data = property(_get_geoip_data)

    class Meta:
        ordering = ('-last_update',)
        unique_together = ('session_key', 'ip_address',)

class UntrackedUserAgent(models.Model):
    keyword = models.CharField(max_length=100, help_text='Part or all of a user-agent string.  For example, "Googlebot" here will be found in "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" and that visitor will not be tracked.')

    def __unicode__(self):
        return self.keyword

    class Meta:
        ordering = ('keyword',)
        verbose_name = 'Untracked User-Agent'
        verbose_name_plural = 'Untracked User-Agents'

class BannedIP(models.Model):
    ip_address = models.IPAddressField('IP Address', help_text='The IP address that should be banned')

    def __unicode__(self):
        return self.ip_address

    class Meta:
        ordering = ('ip_address',)
        verbose_name = 'Banned IP'
        verbose_name_plural = 'Banned IPs'
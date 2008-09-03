from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render_to_response
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from tracking.models import Visitor, UntrackedUserAgent, BannedIP
from tracking import utils
from datetime import datetime, timedelta
import random
import time
import re
import urllib, urllib2

title_re = re.compile('<title>(.*?)</title>')

class VisitorTrackingMiddleware:
    """
    Keeps track of your active users.  Anytime a visitor accesses a valid URL,
    their unique record will be updated with the page they're on and the last
    time they requested a page.

    Records are considered to be unique when the session key and IP address
    are unique together.  Sometimes the same user used to have two different
    records, so I added a check to see if the session key had changed for the
    same IP and user agent in the last 5 minutes
    """

    def process_request(self, request):
        # don't process AJAX requests
        if request.is_ajax():
            return

        # create some useful variables
        session_key = request.session.session_key
        ip_address = request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # see if the user agent is not supposed to be tracked
        for ua in UntrackedUserAgent.objects.all():
            # if the keyword is found in the user agent, stop tracking
            if str(user_agent).find(ua.keyword) != -1:
                return

        prefixes = utils.get_untracked_prefixes()
        # don't track media files
        prefixes.append(settings.MEDIA_URL)
        prefixes.append(settings.ADMIN_MEDIA_PREFIX)

        # ensure that the request.path does not begin with any of the prefixes
        validURL = True
        for prefix in prefixes:
            if request.path.startswith(prefix):
                validURL = False
                break

        # if the URL needs to be tracked, track it!
        if validURL:
            # determine what time it is
            now = datetime.now()

            attrs = {
                        'session_key': session_key,
                        'ip_address': ip_address
                    }

            # for some reason, Visitor.objects.get_or_create was not working here
            try:
                visitor = Visitor.objects.get(**attrs)
            except Visitor.DoesNotExist:
                try:
                    # see if there's a visitor with the same IP and user agent
                    # within the last 5 minutes
                    cutoff = now - timedelta(minutes=5)
                    visitor = Visitor.objects.get(
                                    ip_address=ip_address,
                                    user_agent=user_agent,
                                    last_update__gte=cutoff
                                )
                    visitor.session_key = session_key
                except Visitor.DoesNotExist:
                    # it's probably safe to assume that the visitor is brand new
                    visitor = Visitor(**attrs)

            # determine whether or not the user is logged in
            user = request.user
            if isinstance(user, AnonymousUser):
                user = None

            # update the tracking information
            visitor.user = user
            visitor.user_agent = user_agent

            # if the visitor record is new, or the visitor hasn't been here for
            # at least an hour, update their referrer URL
            one_hour_ago = now + timedelta(hours=-1)
            if not visitor.last_update or \
                visitor.last_update <= one_hour_ago:
                visitor.referrer = request.META.get('HTTP_REFERER', 'unknown')

                # reset the number of pages they've been to
                visitor.page_views = 0
                visitor.session_start = now

            visitor.url = request.path
            visitor.page_views += 1
            visitor.last_update = now
            visitor.save()

class VisitorCleanUpMiddleware:
    """
    Clean up old visitor tracking records in the database
    """
    def process_request(self, request):
        timeout = datetime.now() - timedelta(hours=utils.get_cleanup_timeout())
        Visitor.objects.filter(last_update__lte=timeout).delete()

class BannedIPMiddleware:
    """
    Raises an Http404 error for any page request from a banned IP.  IP addresses
    may be added to the list of banned IPs via the Django admin.

    The banned users do not actually receive the 404 error--instead they get
    an "Internal Server Error", effectively eliminating any access to the site.
    """
    def process_request(self, request):
        # compile a list of all banned IP addresses
        ips = [b.ip_address for b in BannedIP.objects.all()]

        # check to see if the current user's IP address is in that list
        if request.META.get('REMOTE_ADDR', '') in ips:
            raise Http404

class GoogleAnalyticsMiddleware:
    """
    This is a server-side version of the Google Analytics tracking.  It should
    be able to track things like requests to RSS feeds and whatnot, but it does
    tend to lose some information, such as where the request is coming from.
    """
    def process_response(self, request, response):
        # get the title from the response if possible
        try:
            title = title_re.search(response.content).group(1)
        except:
            title = ''

        host = request.META.get('HTTP_HOST', '')
        path = request.META.get('PATH_INFO', '/')

        cookie = random.randint(10000000, 99999999)
        rand = random.randint(1000000000, 3188019257283953000)
        today = int(time.mktime(datetime.now().timetuple()))
        small = random.randint(3, 50)

        utmcc = '__utma=%(r1)i.%(r2)i.%(r3)i.%(r3)i.%(r3)i.%(r4)i;+__utmz=%(r1)i.%(r3)i.%(r4)i.%(r4)i.utmscr=%(host)s|utmccn=(referral)|utmcmd=referral|utmcct=%(path)s;' % {
            'r1': cookie,       'r2': rand,         'r3': today,
            'r4': small,        'host': host,       'path': path
        }

        # setup a dictionary of values for use in the query string
        info = {
            'utmwv': 4.3,
            'utmac': settings.GOOGLE_ANALYTICS_ID,
            'utmhn': host,
            'utmp': path,
            'utmr': request.META.get('HTTP_REFERER', '-'),
            'utmcc': utmcc,
            'utmn': random.randint(1000000000, 9999999999),
            'utmcs': 'UTF-8',
            'utmsr': '800x600',                                     # resolution
            'utmsc': '16-bit',                                      # color-depth
            'utmul': 'en-us',                                       # language
            'utmje': '0',                                           # java
            'utmfl': '9.0  r115',                                   # flash
            'utmdt': title,                                         # title
        }

        # put all of the info values where they belong
        url = 'http://www.google-analytics.com/__utm.gif'
        data = '&'.join(['%s=%s' % (k, urllib.quote(str(info[k]))) for k in info])

        # talk to Google Analytics
        conn = urllib2.urlopen('%s?%s' % (url, data))
        conn.read()

        # send the response back to the client
        return response

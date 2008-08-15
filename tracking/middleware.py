from django.core.urlresolvers import reverse
from django.http import Http404
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from tracking.models import Visitor, UntrackedUserAgent, BannedIP
from tracking import utils
from datetime import datetime, timedelta

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

        # get a list of prefixes that shouldn't be tracked
        try:
            prefixes = settings.NO_TRACKING_PREFIXES
        except AttributeError:
            prefixes = []

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

            visitor.url = request.path
            visitor.page_views += 1
            visitor.last_update = now
            visitor.save()

class BannedIPMiddleware:
    """
    Returns an Http404 error for any page request from a banned IP.  IP addresses
    may be added to the list of banned IPs via the Django admin.
    """
    def process_request(self, request):
        # compile a list of all banned IP addresses
        ips = [b.ip_address for b in BannedIP.objects.all()]

        # check to see if the current user's IP address is in that list
        if request.META.get('REMOTE_ADDR', '') in ips:
            raise Http404
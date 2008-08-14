from django.core.urlresolvers import reverse
from django.http import Http404
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from tracking.models import Visitor, BannedIP
from datetime import datetime

class VisitorTrackingMiddleware:
    """
    Keeps track of your active users.  Anytime a visitor accesses a valid URL,
    their unique record will be updated with the page they're on and the last
    time they requested a page.

    Records are considered to be unique when the session key and IP address
    are unique together.
    """

    def process_request(self, request):
        # get a list of prefixes that shouldn't be tracked
        try:
            prefixes = settings.NO_TRACKING_PREFIXES
        except AttributeError:
            prefixes = []

        # ensure that the request.path does not begin with any of the prefixes
        validURL = True
        for prefix in prefixes:
            if request.path.startswith(prefix):
                validURL = False
                break

        # if the URL needs to be tracked, track it!
        if validURL:
            attrs = {
                        'pk': request.session.session_key,
                        'ip_address': request.META.get('REMOTE_ADDR', '')
                    }

            # for some reason, Visitor.objects.get_or_create was not working here
            try:
                visitor = Visitor.objects.get(**attrs)
            except Visitor.DoesNotExist:
                visitor = Visitor(**attrs)

            # determine whether or not the user is logged in
            user = request.user
            if isinstance(user, AnonymousUser):
                user = None

            # update the tracking information
            visitor.user = user
            visitor.url = request.path
            visitor.last_update = datetime.now()
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
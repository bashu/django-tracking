from django import template
from django.conf import settings
from tracking.models import Visitor
from datetime import datetime, timedelta

register = template.Library()

class VisitorsOnSite(template.Node):
    """
    Injects the number of active users on your site as an integer into the context
    """
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        # get any specified timeout from the settings file, or use 5 minutes by default
        try:
            timeout = settings.TRACKING_TIMEOUT
        except AttributeError:
            timeout = 5

        now = datetime.now()
        cutoff = now - timedelta(minutes=timeout)
        context[self.varname] = Visitor.objects.filter(last_update__gte=cutoff).count()
        return ''

def visitors_on_site(parser, token):
    """
    Determines the number of active users on your site and puts it into the context
    """
    try:
        tag, a, varname = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('visitors_on_site usage: {% visitors_on_site as here %}')

    return VisitorsOnSite(varname)
register.tag(visitors_on_site)
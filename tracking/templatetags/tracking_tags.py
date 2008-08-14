from django import template
from tracking.models import Visitor

register = template.Library()

class VisitorsOnSite(template.Node):
    """
    Injects the number of active users on your site as an integer into the context
    """
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        context[self.varname] = Visitor.objects.active().count()
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
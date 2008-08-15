from django.shortcuts import render_to_response
from django.utils.simplejson.encoder import JSONEncoder
from django.http import Http404
from django.template import RequestContext, Context, loader
from tracking.models import Visitor

def update_active_users(request):
    """
    Returns a list of all active users
    """
    if request.is_ajax():
        active = Visitor.objects.active()
        info = {
            'active': active,
            'registered': active.filter(user__isnull=False),
            'guests': active.filter(user__isnull=True),
            'user': request.user
        }

        # render the list of active users
        t = loader.get_template('tracking/_active_users.html')
        c = Context(info)
        users = {'users': t.render(c)}

        return render_to_response('tracking/json.html',
                                  {'json': JSONEncoder().encode(users)},
                                  context_instance=RequestContext(request))
    return Http404
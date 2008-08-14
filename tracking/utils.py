from django.conf import settings

def get_timeout():
    # get any specified timeout from the settings file, or use 5 minutes by
    # default
    try:
        return settings.TRACKING_TIMEOUT
    except AttributeError:
        return 5
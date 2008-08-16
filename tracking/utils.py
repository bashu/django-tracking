from django.conf import settings

def get_timeout():
    # get any specified timeout from the settings file, or use 10 minutes by
    # default
    try:
        return settings.TRACKING_TIMEOUT
    except AttributeError:
        return 10

def get_cleanup_timeout():
    # get any specified visitor clean-up timeout from the settings file, or
    # use 24 hours by default
    try:
        return settings.TRACKING_CLEANUP_TIMEOUT
    except AttributeError:
        return 24

def get_untracked_prefixes():
    # get a list of prefixes that shouldn't be tracked
    try:
        return settings.NO_TRACKING_PREFIXES
    except AttributeError:
        return []
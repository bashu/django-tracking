VERSION = (0, 2, 9)

def get_version():
    "Returns the version as a human-format string."
    return '.'.join([str(i) for i in VERSION])

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES
import sys, os
import tracking

class osx_install_data(install_data):
    # On MacOS, the platform-specific lib dir is /System/Library/Framework/Python/.../
    # which is wrong. Python 2.5 supplied with MacOS 10.5 has an Apple-specific fix
    # for this in distutils.command.install_data#306. It fixes install_lib but not
    # install_data, which is why we roll our own install_data class.

    def finalize_options(self):
        # By the time finalize_options is called, install.install_lib is set to the
        # fixed directory, so we set the installdir to install_lib. The
        # install_data class uses ('install_data', 'install_dir') instead.
        self.set_undefined_options('install', ('install_lib', 'install_dir'))
        install_data.finalize_options(self)

if sys.platform == "darwin":
    cmdclasses = {'install_data': osx_install_data}
else:
    cmdclasses = {'install_data': install_data}

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
tracking_dir = 'tracking'

for path, dirs, files in os.walk(tracking_dir):
    # ignore hidden directories and files
    for i, d in enumerate(dirs):
        if d.startswith('.'): del dirs[i]

    if '__init__.py' in files:
        packages.append('.'.join(fullsplit(path)))
    elif files:
        data_files.append((path, [os.path.join(path, f) for f in files]))

setup(
    name='django-tracking',
    version=tracking.get_version(),
    url='http://code.google.com/p/django-tracking/',
    author='Josh VanderLinden',
    author_email='codekoala@gmail.com',
    license='MIT',
    packages=packages,
    cmdclass = cmdclasses,
    data_files=data_files,
    description="Basic visitor tracking and blacklisting for Django",
    long_description="""
django-tracking is a simple attempt at keeping track of visitors to your
Django-powered Web site.

Features:

 - Tracks the following information about your visitors:
   - Session key
   - IP address
   - User agent
   - Whether or not they are a registered user and logged in
   - Where they came from (http-referer)
   - What page on your site they last visited
   - How many pages on your site they have visited
 - Allows user-agent filtering for visitor tracking
 - Automatic clean-up of old visitor records
 - Can ban certain IP addresses, rendering the site useless to visitors
   from those IP's (great for stopping spam)
 - The ability to have a live feed of active users on your website
 - Template tags to:
   - display how many active users there are on your site
   - determine how many active users are on the same page within your site
"""
)
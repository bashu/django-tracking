``django-tracking`` is a simple attempt at keeping track of visitors to
Django-powered Web sites.  It also offers basic blacklisting capabilities.

The offial repository for ``django-tracking`` is at
http://bitbucket.org/codekoala/django-tracking.  Please file any tickets there.

Features
========

* Tracks the following information about your visitors:

    * Session key
    * IP address
    * User agent
    * Whether or not they are a registered user and logged in
    * Where they came from (http-referer)
    * What page on your site they last visited
    * How many pages on your site they have visited

* Allows user-agent filtering for visitor tracking
* Automatic clean-up of old visitor records
* Can ban certain IP addresses, rendering the site useless to visitors from
  those IP's (great for stopping spam)
* The ability to have a live feed of active users on your website
* Template tags to:

    * display how many active users there are on your site
    * determine how many active users are on the same page within your site

* Optional "Active Visitors Map" to see where visitors are in the world

Requirements
============

As far as I am aware, the only requirement for django-tracking to work is a
modern version of Django.  I developed the project on Django 1.0 alpha 2 and
beta 1.  It is designed to work with the newforms-admin functionality.

If you wish to use a Google Map to display where your visitors are probably at,
you must have a `Google Maps API key
<http://code.google.com/intl/ro/apis/maps/signup.html>`_, which is free.  In
the past, you were required to have a couple of GeoIP API libraries.  Since
version 0.2.11, these dependencies have been replaced with Django's built-in
GIS utilities.  You might want to grab the `GeoLite City binary
<http://www.maxmind.com/app/geolitecity>`_ unless you are a paying MaxMind
customer.  This is the data file that ``django-tracking`` uses to translate an
IP into a location on the planet.  Configuring this feature is discussed later.

Installation
============

Download ``django-tracking`` using *one* of the following methods:

pip
---

You can download the package from the `CheeseShop
<http://pypi.python.org/pypi/django-tracking/>`_ or use::

    pip install django-tracking

to download and install ``django-tracking``.

easy_install
------------

You can download the package from the `CheeseShop <http://pypi.python.org/pypi/django-tracking/>`_ or use::

    easy_install django-tracking

to download and install ``django-tracking``.

Checkout from BitBucket/GitHub/Google Code
------------------------------------------

Use one of the following commands::

    hg clone http://bitbucket.org/codekoala/django-tracking
    git clone http://github.com/codekoala/django-tracking.git
    hg clone http://django-tracking.googlecode.com/hg/ django-tracking

Package Download
================

Download the latest ``.tar.gz`` file from the downloads section and extract it
somewhere you'll remember.

Configuration
=============

First of all, you must add this project to your list of ``INSTALLED_APPS`` in
``settings.py``::

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        ...
        'tracking',
        ...
    )

Run ``manage.py syncdb``.  This creates a few tables in your database that are
necessary for operation.

Depending on how you wish to use this application, you have a few options:

Visitor Tracking
----------------

Add ``tracking.middleware.VisitorTrackingMiddleware`` to your
``MIDDLEWARE_CLASSES`` in ``settings.py``.  It must be underneath the
``AuthenticationMiddleware``, so that ``request.user`` exists.

Automatic Visitor Clean-Up
++++++++++++++++++++++++++

If you want to have Django automatically clean past visitor information out
your database, put ``tracking.middleware.VisitorCleanUpMiddleware`` in your
``MIDDLEWARE_CLASSES``.

IP Banning
----------

Add ``tracking.middleware.BannedIPMiddleware`` to your ``MIDDLEWARE_CLASSES``
in ``settings.py``.  I would recommend making this the very first item in
``MIDDLEWARE_CLASSES`` so your banned users do not have to drill through any
other middleware before Django realizes they don't belong on your site.

Visitors on Page (template tag)
-------------------------------

Make sure that ``django.core.context_processors.request`` is somewhere in your
``TEMPLATE_CONTEXT_PROCESSORS`` tuple.  This context processor makes the
``request`` object accessible to your templates.  This application uses the
``request`` object to determine what page the user is looking at in a template
tag.

Active Visitors Map
===================

If you're interested in seeing where your visitors are at a given point in
time, you might enjoy the active visitor map feature.  Be sure you have added a
line to your main URLconf, as follows::

    from django.conf.urls.defaults import *

    urlpatterns = patterns('',
        ....
        (r'^tracking/', include('tracking.urls')),
        ....
    )

Next, set a couple of settings in your ``settings.py``:

* ``GOOGLE_MAPS_KEY``: Your very own Google Maps API key
* ``TRACKING_USE_GEOIP``: set this to ``True`` if you want to see markers on
  the map
* ``GEOIP_PATH``: set this to the absolute path on the filesystem of your
  ``GeoIP.dat`` or ``GeoIPCity.dat`` or whatever file.  It's usually something
  like ``/usr/local/share/GeoIP.dat`` or ``/usr/share/GeoIP/GeoIP.dat``.
* ``GEOIP_CACHE_TYPE``: The type of caching to use when dealing with GeoIP data:

    * ``0``: read database from filesystem, uses least memory.
    * ``1``: load database into memory, faster performance but uses more
      memory.
    * ``2``: check for updated database.  If database has been updated, reload
      filehandle and/or memory cache.
    * ``4``: just cache the most frequently accessed index portion of the
      database, resulting in faster lookups than ``GEOIP_STANDARD``, but less
      memory usage than ``GEOIP_MEMORY_CACHE`` - useful for larger databases
      such as GeoIP Organization and GeoIP City.  Note, for GeoIP Country,
      Region and Netspeed databases, ``GEOIP_INDEX_CACHE`` is equivalent to
      ``GEOIP_MEMORY_CACHE``. *default*

* ``DEFAULT_TRACKING_TEMPLATE``: The template to use when generating the
  visitor map.  Defaults to ``tracking/visitor_map.html``.

When that's done, you should be able to go to ``/tracking/map/`` on your site
(replacing ``tracking`` with whatever prefix you chose to use in your URLconf,
obviously).  The default template relies upon jQuery for its awesomeness, but
you're free to use whatever you would like.

Usage
=====

To display the number of active users there are in one of your templates, make
sure you have ``{% load tracking_tags %}`` somewhere in your template and do
something like this::

    {% visitors_on_site as visitors %}
    <p>
        {{ visitors }} active user{{ visitors|pluralize }}
    </p>

If you also want to show how many people are looking at the same page::

    {% visitors_on_page as same_page %}
    <p>
        {{ same_page }} of {{ visitors }} active user{{ visitors|pluralize }}
        {% ifequal same_page 1 %}is{% else %}are{% endifequal %} reading this page
    </p>

If you don't want particular areas of your site to be tracked, you may define a
list of prefixes in your ``settings.py`` using the ``NO_TRACKING_PREFIXES``.  For
example, if you didn't want visits to the ``/family/`` section of your website,
set ``NO_TRACKING_PREFIXES`` to ``['/family/']``.

If you don't want to count certain user-agents, such as Yahoo!'s Slurp and
Google's Googlebot, you may add keywords to your visitor tracking in your
Django administration interface.  Look for "Untracked User-Agents" and add a
keyword that distinguishes a particular user-agent.  Any visitors with the
keyword in their user-agent string will not be tracked.

By default, active users include any visitors within the last 10 minutes.  If
you would like to override that setting, just set ``TRACKING_TIMEOUT`` to however
many minutes you want in your ``settings.py``.

For automatic visitor clean-up, any records older than 24 hours are removed by
default.  If you would like to override that setting, set
``TRACKING_CLEANUP_TIMEOUT`` to however many hours you want in your
``settings.py``.

Good luck!  Please contact me with any questions or concerns you have with the
project!

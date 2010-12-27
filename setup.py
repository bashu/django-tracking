#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys, os
import tracking

setup(
    name='django-tracking',
    version=tracking.get_version(),
    description="Basic visitor tracking and blacklisting for Django",
    long_description=open('README.rst', 'r').read(),
    keywords='django, tracking, visitors',
    author='Josh VanderLinden',
    author_email='codekoala at gmail dot com',
    url='http://bitbucket.org/codekoala/django-tracking',
    license='MIT',
    package_dir={'tracking': 'tracking'},
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: Log Analysis",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Page Counters",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",
    ]
)

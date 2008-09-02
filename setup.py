#!/usr/bin/env python

from distutils.core import setup

setup(  name='django-pipes',
        version='0.2',
        description='Django plugin to handle remote-JSON data',
        author='Harish Mallipeddi',
        author_email='harish.mallipeddi@gmail.com',
        url='http://github.com/mallipeddi/django-pipes/',
        packages=['django_pipes', 'django_pipes.middleware'],
        platforms=["any"],
        long_description="This module offers a nice API to access remote JSON resources from within your Django applications. The API is intentionally kept as close as possible to the Django DB-API. So accessing data from a remote JSON API should feel just like an attempt to fetch the data from a database. It is inspired by Ruby on Rails' ActiveResource library.",
     )

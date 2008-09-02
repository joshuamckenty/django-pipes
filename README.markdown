django-pipes
============

This module offers a nice API to access remote JSON resources from within your Django applications. The API is intentionally kept as close as possible to the Django DB-API. So accessing data from a remote JSON API should feel just like an attempt to fetch the data from a database. It is inspired by Ruby on Rails' ActiveResource library.

Author: *Harish Mallipeddi* (harish.mallipeddi@gmail.com)

## TODO ##

* Retry URLs upon failure.
* Better stats - time taken for request, total time taken.
* Supporting the remaining HTTP verbs - PUT, DELETE.

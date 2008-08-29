from django.conf.urls.defaults import *

urlpatterns = patterns('pipes_sample.search.views',
    (r'^$', 'index'),
    (r'^twitter/$', 'twitter'),
)

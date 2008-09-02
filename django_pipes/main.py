from django.utils import simplejson
from django.core.cache import cache
from django.conf import settings

import urllib, urllib2, socket
from time import time

from exceptions import ObjectNotSavedException, ResourceNotAvailableException
from django_pipes import debug_stats

if hasattr(settings, "PIPES_CACHE_EXPIRY"):
    cache_expiry = settings.PIPES_CACHE_EXPIRY
else:
    cache_expiry = 60

# set default socket timeout; otherwise urllib2 requests could block forever.
if hasattr(settings, "PIPES_SOCKET_TIMEOUT"):
    socket.setdefaulttimeout(settings.PIPES_SOCKET_TIMEOUT)
else:
    socket.setdefaulttimeout(10)

class PipeResultSet(list):
    """all() and filter() on the PipeManager class return an instance of this class."""
    def __init__(self, pipe_cls, items):
        super(PipeResultSet, self).__init__(self)
        if isinstance(items, dict) and hasattr(pipe_cls, '__call__'):
            obj = pipe_cls.__call__()
            obj.items.update(_objectify_json(items))
            self.append(obj)
        elif isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and hasattr(pipe_cls, '__call__'):
                    # let's go ahead and create instances of the user-defined Pipe class
                    obj = pipe_cls.__call__()
                    obj.items.update(_objectify_json(item))
                    self.append(obj)
        else:
            self.append(items)

def _objectify_json(i):
    if isinstance(i, dict):
        transformed_dict = JSONDict()
        for key, val in i.iteritems():
            transformed_dict[key] = i[key] = _objectify_json(val)
        return transformed_dict
    elif isinstance(i, list):
        for idx in range(len(i)):
            i[idx] = _objectify_json(i[idx])
    return i

def _log(msg):
    if settings.DEBUG:
        print msg

class JSONDict(dict):
    def __getattr__(self, attrname):
        if self.has_key(attrname):
            return self[attrname]
        else:
            raise AttributeError

class PipeManager(object):
    """
    Manager class for pipes. Provides the same semantics as Django's ORM Manager class.
    Currently only all(), get() and filter() are implemented.
    
    get() & filter() accept:
        params - a dict of (key,value) pairs which are encoded into HTTP GET params 
                 and appended to the URI provided on the Pipe class.
        should_cache - should response be cached after fetching?
    """
    def _set_pipe(self, pipe):
        self.pipe = pipe

    def filter(self, params, should_cache=None, retries=None):
        if hasattr(self.pipe, 'uri'):
            
            # should cache or not?
            if should_cache is None:
                # no per-request caching specified; lets look for cache option on the Pipe class
                if hasattr(self.pipe, 'should_cache'):
                    should_cache = self.pipe.should_cache
                else:
                    should_cache = True
            
            # how many retries?
            if retries is None:
                # no per-request retries configured; lets look for retries option on the Pipe class
                if hasattr(self.pipe, 'retries'):
                    retries = self.pipe.retries
                else:
                    retries = 0
            
            url_string = self.pipe.uri
            if len(params)>0:
                url_string += "?%s" % urllib.urlencode(params)
            _log("Fetching: %s" % url_string)
            url_string = url_string.replace(" ",'')
            
            start = time()
            # Try the cache first
            resp = cache.get(url_string)
            if resp: 
                # Yay! found in cache!
                _log("Found in cache.")
                stop = time()
                debug_stats.record_query(url_string, found_in_cache=True, time=stop-start)
            else: 
                # Not found in cache
                _log("Not found in cache. Downloading...")
                
                attempts = 0
                while True:
                    try:
                        attempts += 1
                        respObj = urllib2.urlopen(url_string)
                        break
                    except urllib2.HTTPError, e:
                        stop = time()
                        debug_stats.record_query(url_string, failed=True, retries=attempts-1, time=stop-start)
                        raise ResourceNotAvailableException(code=e.code, resp=e.read())
                    except urllib2.URLError, e:
                        if attempts <= retries:
                            continue
                            t1 = time() # reset time
                        else: 
                            stop = time()
                            debug_stats.record_query(url_string, failed=True, retries=attempts-1, time=stop-start)
                            raise ResourceNotAvailableException(reason=e.reason)
                        
                resp = respObj.read()
                if should_cache:
                    cache.set(url_string, resp, cache_expiry)
                stop = time()
                debug_stats.record_query(url_string, retries=attempts-1, time=stop-start)

            resp_obj = simplejson.loads(resp)
            return PipeResultSet(self.pipe, resp_obj)
        else:
            return PipeResultSet(self.pipe, [])

    def get(self, params={}, should_cache=None, retries=None):
        rs = self.filter(params, should_cache, retries)
        if rs:
            return rs[0]
        else:
            return None

    def all(self, should_cache=None, retries=None):
        return self.filter({}, should_cache, retries)

    def _save(self, obj):
        "Makes a POST request to the given URI with the POST params set to the given object's attributes."
        if hasattr(self.pipe, 'uri'):
            url_string = self.pipe.uri
            post_params = urllib.urlencode(obj.items)
            _log("Posting to: %s" % url_string)
            try:
                resp = urllib2.urlopen(urllib2.Request(url_string, post_params))
            except urllib2.HTTPError, e:
                raise ObjectNotSavedException(code=e.code, resp=e.read())
            except urllib2.URLError, e:
                raise ObjectNotSavedException(reason=e.reason)
            else:
                resp_obj = simplejson.loads(resp.read())
                return resp_obj
        else:
            return None

class PipeBase(type):
    """Metaclass for all pipes"""
    def __new__(cls, name, bases, attrs):
        # If this isn't a subclass of Pipe, don't do anything special.
        try:
            if not filter(lambda b: issubclass(b, Pipe), bases):
                return super(PipeBase, cls).__new__(cls, name, bases, attrs)
        except NameError:
            # 'Pipe' isn't defined yet, meaning we're looking at our own
            # Pipe class, defined below.
            return super(PipeBase, cls).__new__(cls, name, bases, attrs)

        # Create the class.
        new_class = type.__new__(cls, name, bases, attrs)
        
        mgr = PipeManager()
        new_class.add_to_class('objects', mgr)
        mgr._set_pipe(new_class)
        
        return new_class

class Pipe(object):
    """Base class for all pipes. Users should typically subclass this class to create their pipe."""
    
    __metaclass__ = PipeBase
    uri = None
    
    def __init__(self, **kwargs):
        self.items = dict()
        if len(kwargs) > 0:
            self.items.update(kwargs)
    
    def add_to_class(cls, name, value):
        setattr(cls, name, value)
    add_to_class = classmethod(add_to_class)

    def __getattr__(self, attrname):
        if attrname == '__setstate__':
            # when you unpickle a Pipe object, __getattr__ gets called
            # before the constructor is called
            # this will result in a recursive loop since self.items won't be available yet.
            raise AttributeError
        elif self.items.has_key(attrname):
            return self.items[attrname]
        else:
            raise AttributeError
    
    def __setattr__(self, attrname, attrval):
        if attrname == 'items':
            # items is the only attribute which should be set as a regular instance attribute.
            object.__setattr__(self, attrname, attrval)
        else:
            # for all other attributes, just insert them into the items dict.
            self.items[attrname] = attrval

    def save(self):
        """
        Makes a POST request to the given URI with the POST params set to the class's attributes.
        Throws a ObjectNotSavedException if the request fails.
        """
        return self.objects._save(self)

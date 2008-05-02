from django.utils import simplejson
from django.core.cache import cache
from django.conf import settings

import urllib

if hasattr(settings, "PIPES_CACHE_EXPIRY"):
    cache_expiry = settings.PIPES_CACHE_EXPIRY
else:
    cache_expiry = 60

class PipeResultSet(list):
    """all() and filter() calls on the PipeManager class return an instance of this class."""
    def __init__(self, pipe_cls, items):
        super(PipeResultSet, self).__init__(self)
        if isinstance(items, dict) and hasattr(pipe_cls, '__call__'):
            obj = pipe_cls.__call__()
            obj.__dict__.update(_objectify_json(items))
            self.append(obj)
        elif isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and hasattr(pipe_cls, '__call__'):
                    # let's go ahead and create instances of the user-defined Pipe class
                    obj = pipe_cls.__call__()
                    obj.__dict__.update(_objectify_json(item))
                    self.append(obj)
        else:
            self.append(items)

def _objectify_json(i):
    if isinstance(i, dict):
        transformed_dict = JSONDict()
        for key, val in i.iteritems():
            transformed_dict[key] = i[key] = _objectify_json(val)
        transformed_dict.__dict__.update(i)
        return transformed_dict
    elif isinstance(i, list):
        for idx in range(len(i)):
            i[idx] = _objectify_json(i[idx])
    return i

def _log(msg):
    if settings.DEBUG:
        print msg

class JSONDict(dict):
    pass

class PipeManager(object):
    """
    Manager class for pipes. Provides the same semantics as Django's ORM Manager class.
    Currently only all(), get() and filter() are implemented.
    
    get() & filter() take in params, a dict of key,val pairs which are encoded into HTTP GET params
    and appended to the URI provided on the Pipe class.
    
    """
    def _set_pipe(self, pipe):
        self.pipe = pipe

    def filter(self, params={}):
        if hasattr(self.pipe, 'uri'):
            url_string = self.pipe.uri
            if len(params)>0:
                url_string += "?%s" % urllib.urlencode(params)
            _log("Fetching: %s" % url_string)
            # Try the cache first
            resp = cache.get(url_string)
            if resp: # Yay! found in cache!
                _log("Found in cache.")
            else: # Not found in cache
                _log("Not found in cache. Downloading...")
                resp = urllib.urlopen(url_string).read()
                cache.set(url_string.replace(" ",''), resp, cache_expiry)
            resp_obj = simplejson.loads(resp)
            return PipeResultSet(self.pipe, resp_obj)
        else:
            return PipeResultSet(self.pipe, [])

    def get(self, params={}):
        rs = self.filter(params)
        if rs:
            return rs[0]
        else:
            return None

    def all(self):
        return self.filter({})

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
    
    def add_to_class(cls, name, value):
        setattr(cls, name, value)
    add_to_class = classmethod(add_to_class)

try:
    # Only exists in Python 2.4+
    from threading import local
except ImportError:
    # Import copy of _thread_local.py from Python 2.4
    from django.utils._threading_local import local

class PipesStats(local):
    def __init__(self):
        self.queries = []
    
    def record_query(self, url, found_in_cache):
        self.queries.append({
            'url':url,
            'found_in_cache':found_in_cache,
        })

    def reset(self):
        self.queries = []
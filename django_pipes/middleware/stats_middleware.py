from django.conf import settings

import django_pipes as pipes

class PipesStatsMiddleware:
    def process_response(self, request, response):
        if settings.DEBUG:
            
            queries = pipes.debug_stats.queries
            
            if len(queries) > 0:
                cached_queries = filter(lambda query: query['found_in_cache'], queries)
                failed_queries = filter(lambda query: query['failed'], queries)
                remote_queries = len(queries) - len(cached_queries) - len(failed_queries)
            
                print "\n================== Pipes Usage Summary ==========================="
                print "Total: %d   Found in cache: %d   Fetched from remote: %d   Failed: %d\n" % (
                        len(queries), len(cached_queries),
                        remote_queries, len(failed_queries)
                    )
                for idx, query in enumerate(queries):
                    if query['failed']:
                        status = "FAILED"
                    elif query['found_in_cache']:
                        status = "FETCHED FROM CACHE"
                    else:
                        status = "FETCHED FROM REMOTE"
                    print "%d) %s (%.3f ms) : %s : %d retries" % (
                            idx+1, 
                            status,
                            query['time'], 
                            query['url'], 
                            query['retries']
                    )
                print "====================================================================\n"
        
        return response

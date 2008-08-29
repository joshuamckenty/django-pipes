import pipes
class PipesStatsMiddleware:
    def process_response(self, request, response):
        print "Pipes calls made: %d" % len(pipes.debug_stats.queries)
        return response

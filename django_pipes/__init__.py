from django.conf import settings
from django.core import signals

from django_pipes.stats import PipesStats
debug_stats = PipesStats()

# Register an event that resets pipes debug_stats.queries
# when a Django request is started.
def reset_pipes_queries(**kwargs):
    debug_stats.queries = []
signals.request_started.connect(reset_pipes_queries)

from django_pipes.main import Pipe, PipeManager, ObjectNotSavedException, ResourceNotAvailableException

__all__ = ('Pipe', 'PipeManager')


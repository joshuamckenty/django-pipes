from django.conf import settings

from pipes.stats import PipesStats
debug_stats = PipesStats()

from pipes.main import Pipe, PipeManager, ObjectNotSavedException

__all__ = ('Pipe', 'PipeManager')


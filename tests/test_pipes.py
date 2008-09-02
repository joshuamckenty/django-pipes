import django_pipes as pipes
from django.core.cache import cache


# models
class Book(pipes.Pipe):
    uri = "http://localhost:9090/book/"

class Nada(pipes.Pipe):
    "This resource does not exist on the server."
    uri = "http://localhost:9091/nonexistent/"

class TimesOut(pipes.Pipe):
    uri = "http://localhost:9090/timeout/"

class BookNotCached(pipes.Pipe):
    uri = "http://localhost:9090/book/"
    should_cache = False # default = True

class Flaky(pipes.Pipe):
    uri = "http://localhost:9091/nonexistent/"
    retries = 1

# tests
def test_two_pipes_of_same_kind_with_different_params():
    "Two pipes of the same kind but filtered by different params should give back different result sets."
    b1 = Book.objects.get({'id':1})
    b2 = Book.objects.get({'id':2})
    assert b1.id != b2.id

def test_POST_request():
    b1 = Book(id=1, title="Python in a nutshell")
    r = b1.save()
    assert r == "success"

def test_fetch_nonexistent_resource():
    try:
        nada = Nada.objects.get({'id':1})
    except pipes.ResourceNotAvailableException, e:
        assert True
    else:
        assert False

def test_fetch_timeout():
    try:
        TimesOut.objects.all()
    except pipes.ResourceNotAvailableException, e:
        import socket
        assert hasattr(e, 'reason') and type(e.reason) == socket.timeout
    else:
        assert False

def test_pipes_debug_stats():
    # clean up stuff from previous tests
    pipes.debug_stats.reset()
    cache.delete("http://localhost:9090/book/?id=1")
    
    b1 = Book.objects.get({'id':1})
    queries = pipes.debug_stats.queries
    assert len(queries) == 1
    query1 = queries[0]
    assert query1['url'] == "http://localhost:9090/book/?id=1"
    assert query1['found_in_cache'] == False

    b1 = Book.objects.get({'id':1})
    assert len(queries) == 2
    query2 = queries[1]
    assert query2['url'] == "http://localhost:9090/book/?id=1"
    assert query2['found_in_cache'] == True

def test_pipe_level_caching_option():
    "if the pipe-level caching option is set to False, then it should override the default value of True"
    # clean up
    pipes.debug_stats.reset()
    cache.delete("http://localhost:9090/book/?id=1")
    
    # fetch the book with id = 1
    b1 = BookNotCached.objects.get({'id':1})
    queries = pipes.debug_stats.queries
    query1 = queries[0]
    assert query1['found_in_cache'] == False
    
    # fetch the book with id = 1 again; should not be fetched from cache
    b2 = BookNotCached.objects.get({'id':1})
    query2 = queries[1]
    assert query2['found_in_cache'] == False

def test_request_level_caching_option():
    "if caching is defined at request-level, it should override global default or pipe-level caching if any"

    # clean up stuff from previous tests
    pipes.debug_stats.reset()
    cache.delete("http://localhost:9090/book/?id=1")

    # override global default
    b1 = Book.objects.get({'id':1}, should_cache=False)
    b1 = Book.objects.get({'id':1}, should_cache=False)
    queries = pipes.debug_stats.queries
    assert queries[1]['found_in_cache'] == False
    
    # override pipes-level default
    nb1 = BookNotCached.objects.get({'id':1}, should_cache=True)
    nb1 = BookNotCached.objects.get({'id':1})
    assert queries[3]['found_in_cache'] == True

def test_retries():
    "if fetching fails, should retry."
    
    pipes.debug_stats.reset()
    queries = pipes.debug_stats.queries
    
    # override global default
    try:
        f = Flaky.objects.all()
    except pipes.ResourceNotAvailableException, e:
        assert queries[0]['retries'] == 1

    # override pipes-level default
    try:
        f = Flaky.objects.all(retries=2)
    except pipes.ResourceNotAvailableException, e:
        assert queries[1]['retries'] == 2

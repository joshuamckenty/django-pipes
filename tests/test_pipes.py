import pipes
from django.core.cache import cache

class Book(pipes.Pipe):
    uri = "http://localhost:9090/book/"

def test_two_pipes_of_same_kind_with_different_params():
    'Two pipes of the same kind but filtered by different params should give back different result sets.'
    b1 = Book.objects.get({'id':1})
    b2 = Book.objects.get({'id':2})
    assert b1.id != b2.id

def test_POST_request():
    b1 = Book(id=1, title="Python in a nutshell")
    r = b1.save()
    assert r == "success"

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
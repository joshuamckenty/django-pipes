import pipes

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
        
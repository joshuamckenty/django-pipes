import pipes

def test_two_pipes_of_same_kind_with_different_params():
    'Two pipes of the same kind but filtered by different params should give back different result sets.'
    class Book(pipes.Pipe):
        uri = "http://localhost:9090/book/"
    b1 = Book.objects.get({'id':1})
    b2 = Book.objects.get({'id':2})
    assert b1.id != b2.id

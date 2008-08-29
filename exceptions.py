class PipesBaseException(Exception):
    def __init__(self, error_code, reason=None, resp=None):
        self.error_code = error_code
        self.reason = reason
        self.resp = resp
    
    def __str__(self):
        if self.reason:
            return repr(self.reason)
        else:
            return repr(self.resp)

class ObjectNotSavedException(PipesBaseException):
    pass
class ResourceNotAvailableException(PipesBaseException):
    pass

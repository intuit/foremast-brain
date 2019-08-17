
class AIEngineException(Exception): 
  
    # Raised when an operation attempts a state  
    # transition that's not allowed. 
    def __init__(self, errorCode, msg, info=""): 
        self.errorCode = errorCode
        self.msg = msg 
        self.info = info
try: 
    raise(TransitionError(2,3*2,"Not Allowed")) 
  
# Value of Exception is stored in error 
except AIEngineException as exception: 
    print('Exception occured: ',exception.msg) 
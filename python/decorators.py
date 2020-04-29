from flask import flash, session
from functools import wraps

def login_required(function_to_protect):
    @wraps(function_to_protect)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id:
            
            if True: # check if session id is valid
                # Success!
                return function_to_protect(*args, **kwargs)
            else:
                pass
                # Session is invalid
        else:
            pass
            # redirect to login
    return wrapper
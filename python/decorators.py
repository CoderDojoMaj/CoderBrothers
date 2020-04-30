from flask import flash, session, redirect, abort
from functools import wraps
from python.db import getDB, UserNotFoundError

def login_required(_func=None, *, perms_level=0):
    def login_required_decorator(function_to_protect):
        @wraps(function_to_protect)
        def wrapper(*args, **kwargs):
            user_id = session.get('user')[0]
            if user_id:
                try:
                    uuid = getDB().getUserUUIDFromSession(user_id) # check if session id is valid
                    perms = getDB().getUserPerms(uuid)
                    # Success!
                    if perms >= perms_level:
                        return function_to_protect(uuid, *args, **kwargs)
                    else:
                        abort(403, f'Not enough permissions')
                except UserNotFoundError:
                    session['user'] = None
                    return redirect('/login'), 401
                    # Session is invalid, redirect to login
            else:
                return redirect('/login'), 401
                # redirect to login
        return wrapper
    if _func is None:
        return login_required_decorator
    else:
        return login_required_decorator(_func)
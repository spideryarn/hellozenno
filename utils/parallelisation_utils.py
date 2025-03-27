import threading
from functools import wraps


def fire_and_forget(f):
    """
    Decorator to run any function in a background thread.
    The caller will continue execution immediately, while the decorated function runs in the background.
    """

    @wraps(f)
    def wrapped(*args, **kwargs):
        thread = threading.Thread(target=f, args=args, kwargs=kwargs)
        thread.daemon = True  # Thread will be terminated when main program exits
        thread.start()
        return thread  # Optionally return the thread object if caller wants to track it

    return wrapped

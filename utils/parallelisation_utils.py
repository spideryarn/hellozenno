import threading
import time
from functools import wraps


def fire_and_forget(f=None, *, delay=0):
    """
    Decorator to run any function in a background thread.
    The caller will continue execution immediately, while the decorated function runs in the background.

    Args:
        f: The function to decorate
        delay: Optional delay in seconds before executing the function

    Usage:
        @fire_and_forget
        def my_function(): ...

        @fire_and_forget(delay=5)
        def delayed_function(): ...
    """

    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            def delayed_func():
                if delay > 0:
                    time.sleep(delay)
                func(*args, **kwargs)

            thread = threading.Thread(target=delayed_func)
            thread.daemon = True  # Thread will be terminated when main program exits
            thread.start()
            return thread  # Optionally return the thread object if caller wants to track it

        return wrapped

    # Handle both @fire_and_forget and @fire_and_forget(delay=5) syntax
    if f is None:
        return decorator
    return decorator(f)


def run_async(func, *args, delay=0, **kwargs):
    """
    Run any function asynchronously without decorating it.

    Args:
        func: The function to run asynchronously
        *args: Positional arguments to pass to the function
        delay: Optional delay in seconds before executing the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        thread: The thread object running the function

    Usage:
        # Run synchronously
        a_slow_function()

        # Run asynchronously
        run_async(a_slow_function)

        # Run asynchronously with arguments
        run_async(a_slow_function, arg1, arg2, kwarg1='value')

        # Run asynchronously with delay
        run_async(a_slow_function, delay=5)
    """

    def delayed_func():
        if delay > 0:
            time.sleep(delay)
        func(*args, **kwargs)

    thread = threading.Thread(target=delayed_func)
    thread.daemon = True
    thread.start()
    return thread

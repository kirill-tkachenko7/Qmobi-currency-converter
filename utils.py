import datetime as dt
from typing import Callable, Any, TypeVar
from functools import wraps
Func = TypeVar('Func', bound=Callable[..., Any])


def cache_results(storage_time: int = 60) -> Callable[[Func], Func]:
    """Cache function return value for a given amount of time (in seconds)."""

    # cache is a dictionary of the following structure:
    # {
    #   (args, kwargs): {
    #       'timestamp': <time when results were added to cache>,
    #       'result': <return value of func(args, kwargs)>
    #   }
    # }

    def _decorator(func: Func) -> Func:
        # make cache accessible from the function
        cache = func.cache = dict()
        @wraps(func)
        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            # if function was called with the same arguments
            # less than storage_time seconds ago, return the cached result
            if args in cache:
                if dt.datetime.now() - cache[args]['timestamp'] <= dt.timedelta(seconds=storage_time):
                    return cache[args]['result']
            # otherwise, run function and store result in cache
            print(f'new cache at key: {args}')
            cache[args] = dict()
            result = func(*args, **kwargs)
            # check if func call cleared the cache, and if not, save the result
            if args in cache:
                cache[args]['timestamp'] = dt.datetime.now()
                cache[args]['result'] = result
            return result
        return _wrapper
    return _decorator
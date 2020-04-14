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
            cache_key = (args, frozenset(kwargs.items()))
            # if function was called with the same arguments
            # less than storage_time seconds ago, return the cached result
            if cache_key in cache:
                if dt.datetime.now() - cache[cache_key]['timestamp'] <= dt.timedelta(seconds=storage_time):
                    return cache[cache_key]['result']
            # otherwise, run function and store result in cache
            print(f'new cache at cache_key: {cache_key}')
            cache[cache_key] = dict()
            cache[cache_key]['timestamp'] = dt.datetime.now()
            result = func(*args, **kwargs)
            cache[cache_key]['result'] = func(*args, **kwargs)
            return result
        return _wrapper
    return _decorator
from typing import Any, Callable
from responses import build_param_error


def validate(key: str, value: Any, message: str, func: Callable[..., Any], invalid_params: list) -> None:
    """Validate value using func.

    func must run successfully if value is valid and raise ValueError if it's invalid.
    if a value is invalid, an error dict is built using build_param_error and appended
    to invalid_params list.
    """
    try:
        func(value)
    except ValueError:
        invalid_params.append(build_param_error(
            name=key, value=value, description=message))


def validate_currency(currency: str) -> None:
    """Raise value error if currency has more or less than 3 letters.

    A check for ISO format would require an extarnal resource, so it
    is left for the exchange rates API, which will return error if either
    currency is in wrong format, or the API does not provide exchange rates
    for it.
    """
    if len(currency) != 3:
        raise ValueError
from typing import Any, Union, Optional

def build_error(status: int, title: str, 
                detail: Optional[Union[list, dict, str]] = None) -> dict:
    """Return a dictionary describing the error.

    Schema:
    {
        'error': {
            'status': "HTTP status code"
            'title': "short title"
            'detail': "An optional string, list or dictionary with error details"
        }
    }
    """
    error = {
        'error': {
            'status': status,
            'title': title,
        }
    }
    if detail:
        error['error']['detail'] = detail
    return error

def build_param_error(name: str, value: Any, description: str) -> dict:
    """Return a dictionary describing a parameter error.

    Can be used in build_error as detail.
    Schema:
    {
        'parameter': {
            'name': name of a parameter
            'value': value of the parameter
        },
        'description': "explanation/reason why a parameter is invalid"
    }
    """
    error = {
        'parameter': {
            'name': name,
            'value': value
        },
        'description': description
    }
    return error
"""A simple server which runs on localhost and provides an API for currency conversion.

To convert currencies, send a GET request to 127.0.0.1:80/api/converter.json
and provide the below parameters. All of them are optional with defaults.

base_currency: a 3-letter ISO-format currency code from which the amount is converted. 
For example, if you want to convert US dollars to Russian roubles, specify base_currency=USD.
If base currency is not USD, a cross rate will be used (i.e. base_currency to USD to quote_currency)
Default value is USD.

quote_currency: a 3-letter ISO-format currency code into which you convert the amount. 
For example, if you want to convert US dollars to Russian roubles, specify quote_currency=RUB.
Default value is RUB. 

amount: amount of base_currency. Can be negative and include a decimal separator "."
Default value is 1.

date: if you need a historical rate, you can specify a date in YYYY-MM-DD format. The rate
at that date will be used for calculation.
Default is None, in which case most recent rate is used (updated hourly). 

API responds with a JSON including request parameters (or defaults), exchange rate and result of conversion.
IF there is an error, JSON with error data is returned.

Example:
Request: GET "/api/converter.json?base_currency=EUR&quote_currency=RUB&amount=1000&date=2020-04-13 HTTP/1.1"
Response:
200 -
{
    "base": "EUR",
    "quote": "RUB",
    "date": "2020-04-13",
    "amount": 1000.0,
    "rate": 80.41336970456744,
    "converted_amount": 80413.36970456745
}

Example of error return:
Request: GET "/api/converter.json?base_currency=EURS&quote_currency=RUBS&amount=-asdf&date=2020-04-13asdf HTTP/1.1"
Response:
400 -
{
    "error": {
        "status": 400,
        "title": "Invalid parameter",
        "detail": [
            {
                "parameter": {
                    "name": "amount",
                    "value": "-asdf"
                },
                "description": "Amount must be integer or float"
            },
            {
                "parameter": {
                    "name": "date",
                    "value": "2020-04-13asdf"
                },
                "description": "Must be in YYYY-MM-DD format"
            },
            {
                "parameter": {
                    "name": "base_currency",
                    "value": "EURS"
                },
                "description": "Must be in 3-letter ISO format"
            },
            {
                "parameter": {
                    "name": "quote_currency",
                    "value": "RUBS"
                },
                "description": "Must be in 3-letter ISO format"
            }
        ]
    }
}

"""


from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
import datetime as dt
import json
from converter import CurrencyConverter
import settings
from responses import build_error, build_param_error
from typing import Any, Callable
from validation import validate, validate_currency


class RequestHandler(BaseHTTPRequestHandler):
    converter = CurrencyConverter()

    def do_GET(self) -> None:
        """Handles GET requests.

        if requested resource is /api/converter.json, returns
        JSON with currency conversion result or with error data.
        For all other paths sends 404 error.
        """
        if '/api/converter.json' in self.path:
            params = self._get_params()
            invalid_params = self._validate_params(params)
            if len(invalid_params):
                response = build_error(
                    400,
                    "Invalid parameter",
                    invalid_params
                )
            else:
                self._fix_params(params)
                response = self.converter.convert(**params)
            
            if 'error' in response:
                self.send_response(response['error']['status'])
                self.send_header('content-type', 'application/problem+json')
            else:
                self.send_response(200)
                self.send_header('content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response, indent=4), 'utf-8'))
        else:
            self.send_error(404)

    def _get_params(self) -> dict:
        """Return a dictionary with GET parameters.

        If therer are no GET parameters, return an empty dictionary.
        """
        query = urlparse(self.path).query
        if query:
            return dict(param.split('=') for param in query.split('&'))
        else:
            return dict()

    def _fix_params(self, params) -> None:
        """Convert GET params to correct type or format.

        All params must be valid for this method to work.
        """
        if params.get('amount'): 
            params['amount'] = float(params['amount'])
        if params.get('base_currency'):
            params['base_currency'] = params['base_currency'].upper()
        if params.get('quote_currency'):
            params['quote_currency'] = params['quote_currency'].upper()
    def _validate_params(self, params: dict) -> list:
        """Validate amount, date, base_currency and quote_currency

        return a list of error items (see validate function)
        """
        invalid_params = list()
        if params.get('amount'):
            validate('amount', params['amount'], "Amount must be integer or float",
                    float, invalid_params)
        if params.get('date'):
            validate('date', params['date'], "Must be in YYYY-MM-DD format",
                    dt.date.fromisoformat, invalid_params)
        if params.get('base_currency'):
            validate('base_currency', params['base_currency'], "Must be in 3-letter ISO format",
                    validate_currency, invalid_params)
        if params.get('quote_currency'):
            validate('quote_currency', params['quote_currency'], "Must be in 3-letter ISO format",
                    validate_currency, invalid_params)
        return invalid_params


# create a ThreadingHTTPServer to enable KeyboardInterrupt
# HTTPServer would deadlock in this case
server = ThreadingHTTPServer(
    (settings.IP_ADDRESS, settings.PORT), RequestHandler)
server.serve_forever(poll_interval=0.1)
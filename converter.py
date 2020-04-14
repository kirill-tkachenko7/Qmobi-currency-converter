import http.client
import json
import datetime as dt
import os
from utils import cache_results
from typing import Union, Any
from responses import build_error

# TODO store in env
APP_ID = '51b21c5160074b08b63d560c40524987'


class CurrencyConverter:
    def __init__(self):
        self.connection = http.client.HTTPConnection('openexchangerates.org')

    # OpenExchangeRates give hourly rates.
    # Therefore, no need to fetch rates from it more often than once an hour.
    @cache_results(storage_time=3600)
    def fetch_USD_rates(self, date: str = None) -> dict:
        """Get all exchange rates for a given base currency for a given date.

        If date is not provided, return latest exchange rates.
        """
        if date:
            source = f'historical/{date}.json'
        else:
            source = 'latest.json'

        try:
            self.connection.request(
                'GET', f'/api/{source}?app_id={APP_ID}')
            response = self.connection.getresponse()
        except:
            # clear cache to be able to try again later.
            self.fetch_USD_rates.cache.pop((self, date))
            return build_error(
                503,
                'Service Unavailable',
                'Failed to get response from downstream server'
            )

        data = json.loads(response.read())
        return data

    def convert(self, amount: float = 1, base_currency: str = 'USD',
                quote_currency: str = 'RUB', date: str = None, **kwargs: Any) -> dict:
        """Convert amount in base currency into amount in quote currency.

        If base currency is not USD, get a cross rate from openexchangerates.org
        and then convert the amount.
        if openexchangerates.org returned an error, re-return that error, but convert it
        to our JSON schema.
        """
        data = self.fetch_USD_rates(date)
        if 'error' in data:
            return build_error(status=data['status'], title=data['message'], detail=data['description'])

        rates = data['rates']
        from_rate = rates.get(base_currency)
        if not from_rate:
            return build_error(
                404,
                'Rate not found',
                {
                    'parameter': base_currency,
                    'description': 'Make sure currency is in a 3-letter ISO format'
                }
            )
        to_rate = rates.get(quote_currency)
        if not to_rate:
            return build_error(
                404,
                f'Rate not found',
                {
                    'parameter': quote_currency,
                    'description': 'Make sure currency is in a 3-letter ISO format'
                }
            )

        rate = to_rate/from_rate
        converted_amount = rate * amount

        return {
            'base': base_currency,
            'quote': quote_currency,
            'date': date,
            'amount': amount,
            'rate': rate,
            'converted_amount': converted_amount,
        }
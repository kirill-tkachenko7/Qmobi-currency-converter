import http.client
import json
import datetime as dt
import os
from utils import cache_results
from typing import Union, Any

# TODO store in env
APP_ID = '51b21c5160074b08b63d560c40524987'

class CurrencyConverter:
    # TODO error handling
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
            raise RuntimeError
            self.connection.request(
                'GET', f'/api/{source}?app_id={APP_ID}')
            response = self.connection.getresponse()
            data = json.loads(response.read())
            return data
        except:
            # clear cache
            self.fetch_USD_rates.cache[(self,date)].pop()
            return self.build_error(
                503,
                'Service Unavailable',
                'Failed to get response from downstream server'
            ) 

    def convert(self, amount: float=1, base_currency: str = 'USD', 
                quote_currency: str = 'RUB', date: str = None) -> dict:
        rates = self.fetch_USD_rates(date)
        if 'error' in rates:
            return rates
        
        from_rate = rates.get(base_currency)
        if not from_rate:
            return self.build_error(
                404,
                'base_currency rate not found',
                'Make sure you specify currency in a 3-letter ISO format'
            )
        to_rate = rates.get(quote_currency)
        if not to_rate:
            return self.build_error(
                404,
                'quote_currency rate not found',
                'Make sure you specify currency in a 3-letter ISO format'
            )

        rate = to_rate/from_rate
        converted_amount = rate * amount

        return self.build_response(
            amount,
            base_currency,
            quote_currency,
            date,
            rate,
            converted_amount
        )

    def build_error(self, status: int, message: str, description: str) -> dict:
        error = {
            'error': True,
            'status': status,
            'message': message,
            'description': description,
        }
        return error
    
    def build_response(self, amount: int, base_currency: str, 
                       quote_currency: str, date: str, exchange_rate: float, 
                       converted_amount: float) -> dict:
        response = {
            'date': date,
            'base': base_currency,
            'quote': quote_currency,
            'rate': exchange_rate,
            'base_amount': amount,
            'quote_amount': converted_amount
        }
        return response
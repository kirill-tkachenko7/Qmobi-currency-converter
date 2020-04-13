import http.client
import json
import datetime as dt
import os
from utils import cache_results

# TODO store in env
APP_ID = '51b21c5160074b08b63d560c40524987'

class CurrencyConverter:
    # TODO error handling
    def __init__(self):
        self.connection = http.client.HTTPConnection('openexchangerates.org')

    @cache_results(storage_time=3600)
    def fetch_rates(self, base_currency: str, date: dt.date = None) -> dict:
        """Get all exchange rates for a given base currency for a given date.

        If date is not provided, return latest exchange rates.
        """
        if date:
            source = f'historical/{date.isoformat()}.json'
        else:
            source = 'latest.json'
        self.connection.request(
            'GET', f'/api/{source}?app_id={APP_ID}&base={base_currency}')
        response = self.connection.getresponse()
        data = json.loads(response.read())
        return data.get('rates')

    def get_rate(self, currency_from: str, currency_to: str, 
                 date: dt.date = None) -> float:
        rates = self.fetch_rates(currency_from, date)
        return rates.get(currency_to)

    def convert(self, amount: float, currency_from: str = 'USD', 
                currency_to: str = 'RUB', date: dt.date = None) -> float:
        rate = self.get_rate(currency_from, currency_to, date)
        return amount * rate
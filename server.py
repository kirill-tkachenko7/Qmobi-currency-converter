from converter import CurrencyConverter
import datetime as dt
import http.server

converter = CurrencyConverter()
print(converter.convert(100, 'USD', 'RUB', dt.date.fromisoformat('2015-02-28')))

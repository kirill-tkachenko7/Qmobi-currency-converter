from converter import CurrencyConverter
import datetime as dt

converter = CurrencyConverter()
print(converter.convert(100, 'USD', 'RUB', dt.date.fromisoformat('2014-11-12')))

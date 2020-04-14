from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
import datetime as dt
import json
from converter import CurrencyConverter
import settings


class RequestHandler(BaseHTTPRequestHandler):
    converter = CurrencyConverter()
    def do_GET(self):
        print(urlparse(self.path).query)
        if '/api/converter.json' in self.path:
            query = urlparse(self.path).query
            if query:
                params = dict(param.split('=') for param in query.split('&'))
                if params.get('date'):
                    dt.date.fromisoformat(params['date'])
                if params.get('amount'):
                    params['amount'] = float(params['amount'])
            else:
                params = dict()
            params['converted amount'] = self.converter.convert(**params)
            self.send_response(200)
            self.send_header('content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(params, indent=4), 'utf-8'))
        else:  
            self.send_response(404)


server = ThreadingHTTPServer((settings.IP_ADDRESS, settings.PORT), RequestHandler)
server.serve_forever(poll_interval=0.1)
# thread = Thread(name='HTTPServer', target = server.serve_forever, daemon = True)
# try:
#     thread.start()
# except KeyboardInterrupt:
#     server.shutdown()
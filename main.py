import http.server
import socketserver
import urllib.request
import os

TELEGRAM_API_URL = "https://api.telegram.org"

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self._proxy_request('GET')

    def do_POST(self):
        self._proxy_request('POST')

    def _proxy_request(self, method):
        url = TELEGRAM_API_URL + self.path

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        req = urllib.request.Request(url, data=body, method=method)
        for key, value in self.headers.items():
            if key.lower() not in ['host', 'connection', 'content-length']:
                req.add_header(key, value)

        try:
            with urllib.request.urlopen(req) as response:
                self.send_response(response.status)
                for key, value in response.getheaders():
                    if key.lower() not in ['connection', 'content-encoding', 'transfer-encoding']:
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Proxy error: {e}".encode())

PORT = int(os.environ.get("PORT", 3000))

with socketserver.TCPServer(("0.0.0.0", PORT), ProxyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
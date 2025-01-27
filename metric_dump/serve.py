from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json

def create_handler_class(dump_file):
    class handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()

            query = parse_qs(urlparse(self.path).query)
            print(f"Incoming GET query {query}")

            dump_file.write(f"{query}\n")


            message = "Hello, World! Here is a GET response"
            self.wfile.write(bytes(message, "utf8"))

        def do_POST(self):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()

            length = int(self.headers.get('content-length'))
            field_data = self.rfile.read(length)
            field_string = str(field_data,"UTF-8")
            fields = json.loads(field_string)
            print(f"Incoming POST: {fields}")
            dump_file.write(f"{field_string}\n")


            message = "Hello, World! Here is a POST response"
            self.wfile.write(bytes(message, "utf8"))

    return handler

def run():
    with open("data_dump.log", "a") as fh:
        with HTTPServer(('', 22222), create_handler_class(fh)) as server:
            server.serve_forever()


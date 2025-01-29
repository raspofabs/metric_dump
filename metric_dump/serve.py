from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import click
import contextlib
import os
import json

def create_handler_class(file_path):
    file_path = Path(file_path)
    is_new = not file_path.is_file()
    dump_file = open(file_path, "a")
    if is_new:
        dump_file.write("[")

    def write_log_line(loggable):
        dump_file.write(f"{loggable},\n")
        dump_file.flush()

    class handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()

            query = parse_qs(urlparse(self.path).query)
            print(f"Incoming GET query {query}")

            write_log_line(f"{query}\n")
            dump_file.flush()

        def do_POST(self):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()

            length = int(self.headers.get('content-length'))
            field_data = self.rfile.read(length)
            field_string = str(field_data,"UTF-8")
            fields = json.loads(field_string)
            print(f"Incoming POST: {fields}")
            write_log_line(f"{field_string}\n")

    return handler


@click.command()
@click.option("-c", "--clean", default=False, is_flag=True, help="whether to start with a fresh log file")
@click.option("-o", "--output", default="data_dump.log", help="location to put the log file")
def run(clean: bool, output: str):
    if clean:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(output)
    with HTTPServer(('', 22222), create_handler_class(output)) as server:
        server.serve_forever()

if __name__ == "__main__":
    run()

from concurrent import futures
import logging
import math
import time
import sqlite3
import threading

import grpc
import service_pb2
import service_pb2_grpc

from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
import socketserver
import json
import cgi

lock = threading.Lock()

class TempLoggingServicer(service_pb2_grpc.TempLoggingServicer):

    def LogTemp(self, request, context):
        logging.warning('Received request: %s', request)
        with lock:
            with sqlite3.connect("data.db") as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO temps VALUES (?,?,?,?)", (request.channel, request.temp, request.humidity, time.time()))
                connection.commit()
                #rows = cursor.execute("SELECT * FROM temps").fetchall()
                #print(rows)
        return service_pb2.TempLoggingResponse()

class Server(SimpleHTTPRequestHandler):

    def _set_headers(self):
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        if not self.path or self.path == '/':
            # Serve HTML page.
            self.path = 'index.html'
            return SimpleHTTPRequestHandler.do_GET(self)
        elif '/data' not in self.path:
            response, error = 'Not found', True
        else:
            response, error = self._get_temps()

        self.send_response(200 if not error else 400)
        self._set_headers()
        response = response.encode()
        self.wfile.write(response)

    def _get_temps(self):
        with lock:
            with sqlite3.connect("data.db") as connection:
                cursor = connection.cursor()
                rows = cursor.execute("SELECT * FROM temps").fetchall()
        records = []
        for row in rows:
            entry = {'temp': row[1], 'humidity': row[2], 'time': row[3]}
            records.append(entry)

        return json.dumps(records), False

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_TempLoggingServicer_to_server(
            TempLoggingServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

def run():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, Server)
    logging.warning("Starting httpd")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.warning("Closing httpd")

if __name__ == '__main__':
    logging.basicConfig()
    with sqlite3.connect("data.db") as connection:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS temps (channel INTEGER, temp REAL, humidity REAL, time REAL)")
        connection.commit()
    h = threading.Thread(target=run)
    h.start()
    serve()


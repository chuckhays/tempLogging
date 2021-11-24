from concurrent import futures
import logging
import math
import time
import sqlite3

import grpc
import service_pb2
import service_pb2_grpc


class TempLoggingServicer(service_pb2_grpc.TempLoggingServicer):

    def LogTemp(self, request, context):
        logging.warning('Received request: %s', request)
        with sqlite3.connect("data.db") as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO temps VALUES (?,?,?,?)", (request.channel, request.temp, request.humidity, time.time()))
            connection.commit()
            rows = cursor.execute("SELECT * FROM temps").fetchall()
            print(rows)
        return service_pb2.TempLoggingResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_TempLoggingServicer_to_server(
            TempLoggingServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    with sqlite3.connect("data.db") as connection:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS temps (channel INTEGER, temp REAL, humidity REAL, time REAL)")
        connection.commit()
    serve()


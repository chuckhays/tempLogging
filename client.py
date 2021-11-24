from __future__ import print_function

import logging
import random

import grpc
import service_pb2
import service_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = service_pb2_grpc.TempLoggingStub(channel)
        response = stub.LogTemp(service_pb2.TempLoggingRequest(temp = 1.5, channel = 1, humidity = 2.5))
        logging.warning('Response: %s', response)

if __name__ == '__main__':
    logging.basicConfig()
    run()

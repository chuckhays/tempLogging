from __future__ import print_function

import logging
import random

import grpc
import service_pb2
import service_pb2_grpc

import smbus
import time

def run():
    bus = smbus.SMBus(1)
    bus.write_byte(0x40, 0xF5)
    time.sleep(0.3)
    data0 = bus.read_byte(0x40)
    data1 = bus.read_byte(0x40)

    humidity = ((data0 * 256 + data1) * 125 / 65536.0) - 6

    time.sleep(0.3)

    bus.write_byte(0x40, 0xF3)
    time.sleep(0.3)

    data0 = bus.read_byte(0x40)
    data1 = bus.read_byte(0x40)

    cTemp = ((data0 * 256 + data1) * 175.72 / 65536.0) - 46.85
    fTemp = cTemp * 1.8 + 32

    logging.warning("H:%.2f C:%.2f F:%.2f", humidity, cTemp, fTemp)

    with grpc.insecure_channel('192.168.1.85:50051') as channel:
        stub = service_pb2_grpc.TempLoggingStub(channel)
        request = service_pb2.TempLoggingRequest(temp = fTemp, channel = 1, humidity = humidity)
        response = stub.LogTemp(request)
        logging.warning('Request: %s', request)
        logging.warning('Response: %s', response)

if __name__ == '__main__':
    logging.basicConfig()
    run()




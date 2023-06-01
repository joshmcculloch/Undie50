import socket
import time
import json
import math

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.setblocking(False)
sock.bind(('', 10000))


cmd = {
    "fwd": 0.0,
    "ccw": 0
}


clients = dict()

try:

    while True:
        try:
            data, addr = sock.recvfrom(100)
            if addr not in clients:
                print("new client")
            clients[addr] = time.time()

            print(data)

            for client in clients:
                if client != addr:
                    sock.sendto(data,client)

            for client in list(clients):
                if (time.time() - clients[client]) > 1:
                    print("client disconnected")
                    del clients[client]

        except BlockingIOError:
            time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    sock.close()
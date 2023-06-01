import socket
import time
import json


class Connectivity(object):
    
    def __init__(self, ssid, password):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(0.01)
        self.req_state = {}
        self.sockaddr = (0,0)
        self.last_keepalive = 0

        self.sockaddr = socket.getaddrinfo('autonabit.nz', 10000)[0][-1]
        self.keep_alive()
 
    def keep_alive(self):
        if time.time() - self.last_keepalive > 0.5:
            self.send(b'{"connected": true}')
            self.last_keepalive = time.time()
        
    def send(self, data):
        self.socket.sendto(data, self.sockaddr)
        
    
    def parse_mgs(self, buffer):
        self.req_state = json.loads(buffer.decode("ascii"))

    
    def recv_dgram(self):
        try:
            buffer = self.socket.recv(100)
            self.parse_mgs(buffer)
            return True
        except OSError:
            return False
        
    def run(self):
        self.keep_alive()
        return self.recv_dgram()
        
conn = Connectivity('2nd one', 'IthinkNegarknowsit')
while True:
    conn.run()
    print(conn.req_state)

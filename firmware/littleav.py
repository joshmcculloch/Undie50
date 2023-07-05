from machine import Pin, PWM, reset
import time
import socket
import network
import json

class Motors(object):
    
    def __init__(self):
        self.lf = PWM(Pin(16, Pin.OUT))
        self.lb = PWM(Pin(17, Pin.OUT))
        self.rf = PWM(Pin(18, Pin.OUT))
        self.rb = PWM(Pin(19, Pin.OUT))
        
    def map_cmd(self, cmd, clamp=0.90):
        cmd = max(min(cmd, clamp), -clamp)
        return int(cmd * (2**16-1))
    
    def tone(self,freq):
        self.set_freq(freq)
        self.lf.duty_u16(10000)
        self.lb.duty_u16(0)
        self.rf.duty_u16(10000)
        self.rb.duty_u16(0)
        
    def set_freq(self, freq):
        self.lf.freq(freq)
        self.lb.freq(freq)
        self.rf.freq(freq)
        self.rb.freq(freq)

        
    def cmd(self, fwd, turn):
        left = fwd + turn
        right = fwd - turn
        
        if left > 0:
            self.lf.duty_u16(self.map_cmd(left))
            self.lb.duty_u16(0)
        elif left < 0:
            self.lf.duty_u16(0)
            self.lb.duty_u16(self.map_cmd(abs(left)))
            
        if right > 0:
            self.rf.duty_u16(self.map_cmd(right))
            self.rb.duty_u16(0)
        elif right < 0:
            self.rf.duty_u16(0)
            self.rb.duty_u16(self.map_cmd(abs(right)))
            
            
    def stop(self):
        self.lf.duty_u16(0)
        self.lb.duty_u16(0)
        self.rf.duty_u16(0)
        self.rb.duty_u16(0)
        
class Connectivity(object):
    
    def __init__(self, ssid, password):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.ssid = ssid
        self.password = password
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(0.01)
        self.req_state = {}
        self.sockaddr = (0,0)
        self.last_keepalive = 0
        
        
        
    def connect(self):
        self.wlan.connect(self.ssid, self.password)
        while not self.wlan_connected: #self.wlan.isconnected() and self.wlan.status() >= 0:
            print("Waiting to connect:")
            time.sleep(1)
            
        self.sockaddr = socket.getaddrinfo('autonabit.nz', 10000)[0][-1]
        print(self.sockaddr)
        self.keep_alive()
        
        
    def keep_alive(self):
        if time.ticks_diff(time.ticks_ms(), self.last_keepalive) > 500:
            self.send(b'{"connected": true}')
            self.last_keepalive = time.ticks_ms()
        
    def send(self, data):
        self.socket.sendto(data, self.sockaddr)
        
    @property
    def wlan_connected(self):
        return self.wlan.isconnected()
    
    def parse_mgs(self, buffer):
        self.req_state = json.loads(buffer.decode("ascii"))

            
    def recv(self):
        buffer = b""
        recving = True
        while recving:
            try:
                b = self.socket.recv(1)
            except OSError:
                b = b""
                recving = False
            else:
                if b == b"\n":
                    self.parse_mgs(buffer)
                    buffer = b""
                else:
                    buffer += b
    
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
        


def main():

    conn = Connectivity('2nd one', 'IthinkNegarknowsit')
    #conn = Connectivity('3d47', 'canterbury')

    conn.connect()
    m = Motors()
    print(conn.wlan.ifconfig())

    for i in range(100,3000,100):
        m.tone(i)
        time.sleep(0.04)
    m.stop()

    m.set_freq(100)
        
    connected = True
    last_msg = time.time()
    while connected:
        if conn.run():
            last_msg = time.time()
        elif (time.time() - last_msg) > 2:
            connected = False
            print()
            
        if "fwd" in conn.req_state and "ccw" in conn.req_state:
            m.cmd(conn.req_state["fwd"], conn.req_state["ccw"])

    m.stop()

    for i in range(3000,100,-100):
        m.tone(i)
        time.sleep(0.04)

    m.stop()

    reset()


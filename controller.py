

import tkinter as tk
import os
import socket
import time
import threading
import json

os.system('xset r off')

state = {
    "Left": False,
    "Right": False,
    "Up": False,
    "Down": False
}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

running = True

def send_cmd():
    while running:
        send_state()
        time.sleep(0.1)

def send_state():
    cmd = {
        "fwd": (1 if state["Up"] else 0) + (-1 if state["Down"] else 0),
        "ccw": (1 if state["Right"] else 0) + (-1 if state["Left"] else 0)
    }
    data = (json.dumps(cmd)+"\n").encode("ascii")

    sock.sendto(data, ('autonabit.nz', 10000))

def onKeyPress(event):
    if event.keysym in state:
        state[event.keysym] = True
        send_state()
        #print(state)


def onKeyRelease(event):
    if event.keysym in state:
        state[event.keysym] = False
        send_state()
        #print(state)

threading.Thread(target=send_cmd).start()

root = tk.Tk()
root.geometry('300x200')
#text = tk.Text(root, background='black', foreground='white', font=('Comic Sans MS', 12))
#text.pack()
root.bind('<KeyPress>', onKeyPress)
root.bind('<KeyRelease>', onKeyRelease)
root.mainloop()

running = False
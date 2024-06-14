import colorama
import time
import os

class Client:
    
    # Constructor
    def __init__(self, username, ip, port, server_stub):
        self.username = username
        self.ip = ip
        self.port = port
        self.server_stub = server_stub
import grpc
import threading
import tkinter as tk

# Importar classes gRPC
from proto import chat_pb2
from proto import chat_pb2_grpc

class PrivateChat():
    
    # Constructor
    def __init__(self, other_username, other_ip, other_port, other_stub=None):
        self.other_username = other_username
        self.other_ip = other_ip
        self.other_port = other_port
        # Obrir stub o agafar el passat per paràmetre
        if other_stub is None:
            channel = grpc.insecure_channel(f"{other_ip}:{other_port}")
            self.stub = chat_pb2_grpc.ClientServiceStub(channel)
        else:
            self.stub = other_stub
        # Obrir chat privat en un thread
        threading.Thread(target=self.open_chat).start()
        
    def open_chat(self):
        print(f"Chat obert amb '{self.other_username}'")
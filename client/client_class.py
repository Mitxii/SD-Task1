import grpc
import threading
import time
import os

# Importar classes gRPC
from proto import chat_pb2
from proto import chat_pb2_grpc

class Client:
    
    # Constructor
    def __init__(self, username, ip, port, server_stub):
        self.username = username
        self.ip = ip
        self.port = port
        self.server_stub = server_stub
        # Llançar thread per enviar senyals al client
        threading.Thread(target=self.hearbeat_server).start()

    # Mètode per parar el client
    def stop_client(self, message=None):
        os.system("cls" if os.name == "nt" else "clear")
        if message is not None: print(message)
        print("Aturant client...")
        time.sleep(2)
        os._exit(0)

    # Mètode per comprovar l'estat del servidor central mitjançant senyals contínues
    def hearbeat_server(self):
        while True:
            try:
                self.server_stub.Heartbeat(chat_pb2.Empty())
            except grpc.RpcError:
                self.stop_client("El servidor s'ha desconnectat!")
                break
            time.sleep(1)
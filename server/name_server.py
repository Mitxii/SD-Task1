import grpc
import redis
import json
import threading
import time

# Importar classes gRPC
from proto import chat_pb2
from proto import chat_pb2_grpc

# Importar altres classes
from server_log import ServerLog

class NameServer:
    
    # Constructor
    def __init__(self):
        # Inicialitzar logger
        self.logger = ServerLog(self)
        # Connectar a Redis
        self.redis = redis.StrictRedis(host="localhost", port=6379)
        self.redis.delete("clients")
        
    # Mètode per comprovar si un client existeix (està connectat)
    def exists_client(self, username):
        return self.redis.hexists("clients", username)
    
    # Mètode per obtenir les dades de connexió d'un client
    def get_client_info(self, username):
        # Comprovar que existeixi el client
        if not self.exists_client(username):
            self.logger.error(f"No s'ha trobat el client '{username}'")
            return "", 0
        
        client_info = self.redis.hget("clients", username)
        client_info = json.loads(client_info.decode("utf-8"))
        ip = client_info["ip"]
        port = client_info["port"]
        return ip, port
    
    # Mètode per comprovar l'estat dels clients mitjançant senyals contínues
    def heartbeat(self, username):
        # Obtenir dades del client
        ip, port = self.get_client_info(username)
        if ip == "" and port == 0: return
        address = f"{ip}:{port}"
        
        # Esperar a que el client iniciï el servicer i enviar senyals
        time.sleep(3)
        with grpc.insecure_channel(address) as channel:
            stub = chat_pb2_grpc.ClientServiceStub(channel)
            while True:
                try:
                    stub.Heartbeat(chat_pb2.Empty())
                except grpc.RpcError:
                    self.logger.log(f"El client '{username}' s'ha desconnectat")
                    self.redis.hdel("clients", username)
                    break
                time.sleep(1)
    
    # Mètode per registrar un client
    def register_client(self, username, ip, port):
        # Comprovar que el nom d'usuari no estigui buit
        if username.replace(" ", "") == "":
            self.logger.error("No s'ha pogut registrar el client (nom d'usuari buit)")
            return False, "El nom d'usuari no pot estar buit."

        # Comprovar si ja hi ha un client connectat amb el mateix nom d'usuari
        if self.exists_client(username):
            self.logger.error(f"No s'ha pogut registrar el client '{username}' (nom d'usuari en ús)")
            return False, "Aquest nom d'usuari està actualment en ús."
        
        # Registrar client
        client_info = json.dumps({"ip": ip, "port": port})
        self.redis.hset("clients", username, client_info)
        self.logger.success(f"Client registrat {{username: {username}, ip: {ip}, port: {port}}}")
        # Llançar thread per enviar senyals al client
        threading.Thread(target=self.heartbeat, args=(username,)).start()
        return True, ""
    
name_server = NameServer()
        
import grpc
import redis
import json

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
        return True, ""
    
    # Mètode per obtenir tots els clients
    def get_all_clients(self):
        clients = self.redis.hgetall("clients")
        return {username.decode('utf-8'): json.loads(info.decode('utf-8')) for username, info in clients.items()}
    
name_server = NameServer()
        
import grpc
import argparse
import time
import signal
import sys
import pika
from concurrent import futures

# Importar classes gRPC
from proto import chat_pb2
from proto import chat_pb2_grpc

# Importar altres classes
from server_log import ServerLog
from name_server import name_server

class CentralServer(chat_pb2_grpc.CentralServerServicer):
    
    # Constructor
    def __init__(self):
        # Inicialitzar logger
        self.logger = ServerLog(self)
    
    # Mètode per donar senyal de vida
    def Heartbeat(self, request, context):
        return chat_pb2.Empty()
    
    # Mètode per registrar un client
    def RegisterClient(self, request, context):
        username = request.username
        ip = request.ip
        port = request.port
        response = name_server.register_client(username, ip, port)
        return chat_pb2.RegisterResponse(success=response[0], body=response[1])

    # Mètode per obtenir la informació de connexió d'un client
    def GetClientInfo(self, request, context):
        ip, port = name_server.get_client_info(request.username)
        return chat_pb2.GetInfoResponse(ip=ip, port=port)

# Mètode per fer configuracions globals al servidor RabbitMQ
def configure_rabbit(servicer):
    servicer.logger.log("Iniciant servidor RabbitMQ...")
    
    # Connectar-se a RabbitMQ
    credentials = pika.PlainCredentials("user", "password")
    parameters = pika.ConnectionParameters("localhost", 5672, '/', credentials)
    while True:
        try:
            connection = pika.BlockingConnection(parameters)
            servicer.logger.log("Servidor RabbitMQ iniciat. Escoltant al port 5672...")
            break
        except Exception:
            time.sleep(2)
            pass
    channel = connection.channel()
    
    # Crear exchange i cua per al descobriment de chats
    channel.exchange_declare(exchange="chat_discovery", exchange_type="fanout")
    
    # Crear cua pels insults amb timeout de 2 segons
    arguments = {"x-message-ttl": 2000}
    channel.queue_declare(queue="insults", arguments=arguments)
    
    connection.close()

# Mètode per iniciar els servidors
def serve(port):
    servicer = CentralServer()

    # Configurar RabbitMQ
    configure_rabbit(servicer)
    
    # Configurar servidor gRPC
    servicer.logger.log("Iniciant servidor central...")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_CentralServerServicer_to_server(servicer, server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    servicer.logger.log(f'Servidor central iniciat. Escoltant al port {port}...')

    # Funció per gestionar les senyals SIGINT i SIGTERM
    def signal_handler(sig, frame):
        servicer.logger.log("Aturant servidor central...")
        server.stop(0)
        time.sleep(1)
        sys.exit(0)
        
    # Assignar el gestor de senyals per SIGINT i SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Bucle infinit
    while True:
        time.sleep(86400)
        
# Main
if __name__ == "__main__":
    
    # Obtenir arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int)
    port = parser.parse_args().port
    serve(port)
    
    
    
    
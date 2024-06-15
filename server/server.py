import grpc
import argparse
import time
import signal
import sys
import pika
import threading
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
            servicer.logger.log("Servidor RabbitMQ escoltant...")
            break
        except Exception:
            time.sleep(2)
            pass
    channel = connection.channel()
    
    # Crear exchange i cua per al descobriment de chats
    channel.exchange_declare(exchange="chat_discovery", exchange_type="fanout")
    channel.queue_declare(queue="discovery_queue")
    
    # Funció per processar els missatges
    def on_discovery_request(ch, method, properties, body):
        pass
    
    # Consumir missatges
    channel.basic_consume(queue="discovery_queue", on_message_callback=on_discovery_request, auto_ack=True)
    channel.start_consuming()

# Mètode per iniciar el servidor gRPC
def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = CentralServer()
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

    # Configurar RabbitMQ
    threading.Thread(target=configure_rabbit, args=(servicer,)).start()

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
    
    
    
    
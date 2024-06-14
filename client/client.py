import grpc
import colorama
import argparse
import yaml
import re
import time
import os
import signal
from concurrent import futures

# Importar classes gRPC
from proto import chat_pb2
from proto import chat_pb2_grpc

# Importar altres classes
from client_class import Client

class ClientServicer(chat_pb2_grpc.ClientServiceServicer):
    
    # Constructor
    def __init__(self):
        self.client = client
    
    # Mètode per donar senyal de vida
    def Heartbeat(self, request, context):
        return chat_pb2.Empty()
    
    # Mètode per enviar un missatge
    def SendMessage(self, request, context):
        pass
    
    # Mètode per rebre un missatge
    def ReceiveMessage(self, request, context):
        pass

# Mètode per registrar el client al servidor central
def register_client(ip, port):
    # Obtenir dades del fitxer config.yaml
    with open("config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)
    server = config["server"]
    server_ip = server["ip"]
    server_grpc_port = server["grpc_port"]
    
    # Obrir canal gRPC i crear un stub
    channel = grpc.insecure_channel(f"{server_ip}:{server_grpc_port}")
    server_stub = chat_pb2_grpc.CentralServerStub(channel)
    
    # Bucle per obtenir un nom d'usuari disponible
    while True:
        # Demanar nom d'usuari
        username = input("Introdueix usuari: ")
        # Eliminar caràcters especials
        username = re.sub(r"[^A-Za-z0-9\s]", "", username)
        # Registrar client
        response = server_stub.RegisterClient(chat_pb2.RegisterRequest(username=username, ip=ip, port=port))
        if response.success:
            client = Client(username, ip, port, server_stub)
            print(f"{colorama.Back.GREEN} ✔ {colorama.Back.RESET} T'has registrat correctament.")
            break
        else:
            print(f"{colorama.Back.RED} ✖ {colorama.Back.RESET} {response.body}")
            
    return client

# Mètode per iniciar el servicer
def serve(client):
    servicer = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ClientServiceServicer_to_server(ClientServicer(), servicer)
    servicer.add_insecure_port(f'{client.ip}:{client.port}')
    servicer.start()
    
    return servicer

# Main
if __name__ == "__main__":
    
    # Inicialitzar biblioteca de colors per la terminal
    colorama.init()

    # Crear l'analitzador d'arguments per obtenir l'adreça del client (ip:port)
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str)
    parser.add_argument("--port", type=int)
    ip = parser.parse_args().ip
    port = parser.parse_args().port
    
    # Registrar client
    client = register_client(ip, port)
    username = client.username
    
    # Iniciar servicer
    servicer = serve(client)

    # Funció per gestionar les senyals SIGINT i SIGTERM
    def signal_handler(sig, frame):
        client.stop_client()

    # Assignar el gestor de senyals per SIGINT i SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Esperar mig segon i netejar terminal
    time.sleep(0.5)
    os.system("cls" if os.name == "nt" else "clear")
    
    # Missatge de benvinguda
    os.system(f"echo 'Bones, \033[33m{username}\\033]0;{username}\\007\033[0m!'")
    print(f"\n\t{colorama.Back.YELLOW + colorama.Fore.BLACK} [P]rivat | [G]rupal | [D]escobrir | [I]nsults | [S]ortir {colorama.Back.RESET + colorama.Fore.RESET}\n")

    # Bucle principal del client
    while True:
        option = input("Opció: ").upper()
        match option:
            case "P":
                break                
            case "G":
                break
            case "D":
                break
            case "I":
                break
            case "S":
                print(f"Fins aviat {colorama.Fore.YELLOW + username + colorama.Fore.RESET}!")
                break
            case default:
                print(f"{colorama.Back.RED} ✖ {colorama.Back.RESET} Opció invàlida. Tria'n una de vàlida.{colorama.Fore.RESET}")
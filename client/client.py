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
    
    # Mètode per fer una petició de chat privat
    def Connection(self, request, context):
        accept = self.client.connection(request.username)
        return chat_pb2.ConnectionResponse(accept=accept)
        
    # Mètode per enviar un missatge
    def SendMessage(self, request, context):
        username = request.username
        message = request.body
        time = request.time
        self.client.send_message_to(username, message, time)
        return chat_pb2.Empty()

# Mètode per llegir el fitxer de configuració
def read_config(file):
    with open(file, "r") as config_file:
        config = yaml.safe_load(config_file)
        return config["server"]

# Mètode per registrar el client al servidor central
def register_client(ip, port):
    # Obtenir dades del fitxer config.yaml
    server = read_config("config.yaml")
    server_ip = server["ip"]
    server_grpc_port = server["grpc_port"]
    server_rabbit_port = server["rabbit_port"]
    
    # Obrir canal gRPC i crear un stub
    try:
        channel = grpc.insecure_channel(f"{server_ip}:{server_grpc_port}")
        server_stub = chat_pb2_grpc.CentralServerStub(channel)
    except Exception:
        print(f"{colorama.Back.RED} ✖ {colorama.Back.RESET} No s'ha pogut connectar amb el servidor")
        time.sleep(2)
        os._exit(0)
    
    # Bucle per obtenir un nom d'usuari disponible
    while True:
        # Demanar nom d'usuari
        username = input("Introdueix usuari: ")
        # Eliminar caràcters especials
        username = re.sub(r"[^A-Za-z0-9\s]", "", username)
        # Registrar client
        response = server_stub.RegisterClient(chat_pb2.RegisterRequest(username=username, ip=ip, port=port))
        if response.success:
            client = Client(username, ip, port, server_stub, server_ip, server_rabbit_port)
            print(f"{colorama.Back.GREEN} ✔ {colorama.Back.RESET} T'has registrat correctament.")
            break
        else:
            print(f"{colorama.Back.RED} ✖ {colorama.Back.RESET} {response.body}")
            
    return client

# Mètode per iniciar el servicer
def serve(client):
    servicer = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ClientServiceServicer_to_server(ClientServicer(), servicer)
    try:
        servicer.add_insecure_port(f'{client.ip}:{client.port}')
        servicer.start()
    except Exception:
        print(f"{colorama.Back.RED} ✖ {colorama.Back.RESET} S'ha produit un error configurant el Servicer")
        time.sleep(1)
        os._exit(0)
    
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
    def signal_handler(sig, frame, message=None):
        client.stop_client(message)

    # Assignar el gestor de senyals per SIGINT i SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Esperar mig segon i netejar terminal
    time.sleep(0.5)
    os.system("cls" if os.name == "nt" else "clear")
    
    # Mètode per imprimir les opcions de l'aplicació
    def print_options():
        print("\n    ", end="")
        options = ["[P]rivat", "[G]rupal", "[D]escobrir", "[I]nsults", "[N]etejar", "[S]ortir"]
        for index, option in enumerate(options):
            aux = "-"
            if index == len(options) - 1:
                aux = " "
            print(f"{colorama.Back.YELLOW + colorama.Fore.BLACK} {option} {colorama.Back.RESET + colorama.Fore.YELLOW}", end=f"{aux}{colorama.Fore.RESET}")
        print()            
    
    # Missatge de benvinguda
    os.system(f"echo 'Bones, \033[33m{username}\\033]0;{username}\\007\033[0m!'")
    print_options()

    # Bucle principal del client
    while True:
        option = input(f"\n{colorama.Fore.YELLOW}Opció:{colorama.Fore.RESET} ").upper()
        match option:
            case "P":
                # Connectar-se a chat privat
                client.connect_chat()      
            case "G":
                # Subscriure's a chat grupal        
                client.connect_group()
            case "D":
                # Descobrir chats actius
                break
            case "I":
                # Connectar-se al canal d'insults
                break
            case "N":
                # Netejar pantalla i tornar a imprimir les opcions
                os.system("cls" if os.name == "nt" else "clear")
                print_options()
            case "S":
                # Sortir
                signal_handler(None, None, f"Fins aviat {colorama.Fore.YELLOW + username + colorama.Fore.RESET}!")
                break
            case default:
                # Inpupt invàlid
                print(f"{colorama.Back.RED} ✖ {colorama.Back.RESET} Opció invàlida. Tria'n una de vàlida.{colorama.Fore.RESET}")
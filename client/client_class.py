import grpc
import threading
import time
import os
import colorama
import pika
import requests
import tkinter as tk

# Importar classes gRPC
from proto import chat_pb2
from proto import chat_pb2_grpc

# Importar altres classes
from private_chat import PrivateChat
from group_chat import GroupChat
from client_log import ClientLog

class Client:
    
    # Constructor
    def __init__(self, username, ip, port, server_stub, server_ip, server_rabbit_port):
        self.username = username
        self.ip = ip
        self.port = port
        # Dades per gRPC
        self.server_stub = server_stub
        # Dades per RabbitMQ
        self.server_ip = server_ip
        self.server_rabbit_port = server_rabbit_port
        # Chats privats actius
        self.private_chats = {}
        # Chats grupals subscrits i actius
        self.subscribed_chats = {}
        self.group_chats = {}
        # Inicialitzar biblioteca de colors per la terminal
        colorama.init()
        # Llançar thread per enviar senyals al client
        threading.Thread(target=self.hearbeat_server).start()
        # Connectar-se a RabbitMQ
        self.connection, self.channel = self.connect_to_rabbit()
        # Inicialitzar logger
        self.logger = ClientLog()

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
                self.stop_client(f"{colorama.Back.RED} ✖ {colorama.Back.RESET} El servidor s'ha desconnectat!")
                break
            time.sleep(1)
        
    # Mètode per connectar-se a un chat (privat o grupal)    
    def connect_chat(self):
        # Demanar el tipus de chat
        print("A quin tipus de chat et vols connectar? [P]rivat [G]rupal [C]ancel·lar")
        while True:
            option = input().upper()
            match option:
                case "P":
                    # Connectar-se a chat privat
                    self.connect_private_chat()
                    break
                case "G":
                    # Connectar-se a chat grupal
                    self.connect_group_chat()
                    break
                case "C":
                    # Cancel·lar connexió
                    self.logger.success("S'ha cancel·lat la connexió.")
                    return
                case default:
                    # Opció invàlida
                    self.logger.error("Opció invàlida. Tria'n una de vàlida.")
    
    # Mètode per contestar una petició de chat privat
    def connection_request(self, other_username):
        self.accept = False
        
        # Comprovar que no tingui ja un chat obert amb l'altre client
        if other_username in self.private_chats:
            return False
        
        # Funció per respondre una sol·licitud de chat (acceptar o denegar)
        def answer_connection(bool):
            root.destroy()
            if bool:
                # Obtenir dades de l'altre client
                response = self.server_stub.GetClientInfo(chat_pb2.GetInfoRequest(username=other_username))
                other_ip = response.ip
                other_port = response.port
                if other_ip == "" and other_port == 0:
                    bool = False
                else:
                    # Crear i guardar chat privat
                    chat = PrivateChat(self, other_username, other_ip, other_port)
                    self.private_chats[other_username] = chat
            # Guardar resultat
            self.accept = bool
        
        # Configurar finestra per respondre la sol·licitud
        root = tk.Tk()
        root.title(f"[{self.username}] Petició de chat")
        root.geometry("350x90")
        tk.Label(root, text=f"L'usuari '{other_username}' vol iniciar un chat privat.").pack(pady=(5, 0))
        # Frame pels botons d'acceptar i denegar
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        deny_btn = tk.Button(btn_frame, text="Denegar", command=lambda: answer_connection(False), bg="#B22222", cursor="hand2")
        deny_btn.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        tk.Label(btn_frame, width=10).pack(side=tk.LEFT)
        accept_btn = tk.Button(btn_frame, text="Acceptar", command=lambda: answer_connection(True), bg="#008000", cursor="hand2")
        accept_btn.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)

        # Llançar finestra
        root.mainloop()
        
        return self.accept
            
    # Mètode per fer una petició de chat privat   
    def connect_private_chat(self):
        other_username = input("Introdueix el nom d'usuari:\n")
        
        # Comprovacions inicials
        if other_username == self.username:
            self.logger.error("No pots iniciar un chat privat amb tu mateix.")
            return
        elif other_username in self.private_chats:
            self.logger.error("Ja tens un chat obert amb aquest usuari.")
            return
        
        # Obtenir dades de l'altre client
        print("Obtenint dades...")
        response = self.server_stub.GetClientInfo(chat_pb2.GetInfoRequest(username=other_username))
        other_ip = response.ip
        other_port = response.port
        if other_ip == "" and other_port == 0:
            self.logger.error("No s'ha trobat l'usuari.")
            return
        else:
            self.logger.success("S'ha trobat l'usuari.")

        # Sol·licitar chat privat
        print("Sol·licitant chat privat...")
        channel = grpc.insecure_channel(f"{other_ip}:{other_port}")
        other_stub = chat_pb2_grpc.ClientServiceStub(channel)
        response = other_stub.Connection(chat_pb2.ConnectionRequest(username=self.username))
        if not response.accept:
            self.logger.error("L'altre usuari ha denegat la petició o encara té el chat anterior obert.")
        else:
            self.logger.success("L'altre usuari ha acceptat la petició.")
            # Crear i guardar chat privat
            print("Obrint chat...")
            chat = PrivateChat(self, other_username, other_ip, other_port)
            self.private_chats[other_username] = chat
    
    # Mètode per tancar un chat privat    
    def close_chat(self, other_username):
        if other_username in self.private_chats:
            self.private_chats.pop(other_username)
           
    # Mètode per enviar un missatge 
    def send_message_to(self, other_username, message, time):
        if other_username in self.private_chats:
            chat = self.private_chats[other_username]
            # Enviar missatge
            chat.display_message(message, time, "left")
            
    # Mètode per connectar-se a RabbitMQ
    def connect_to_rabbit(self):
        credentials = pika.PlainCredentials("user", "password")
        parameters = pika.ConnectionParameters(self.server_ip, self.server_rabbit_port, '/', credentials)
        while True:
            try:
                connection = pika.BlockingConnection(parameters)
                break
            except Exception:
                pass
        channel = connection.channel()
        return connection, channel
    
    # Mètode per saber si un chat grupal és persistent
    def is_exchange_persistent(self, exchange_name):
        # Configurar URL de la API de gestió de RabbitMQ
        url = f'http://user:password@{self.server_ip}:15672/api/exchanges/%2F/{exchange_name}'
        
        # Fer la crida GET a la API
        response = requests.get(url)
        if response.status_code == 200:
            exchange_info = response.json()
            arguments = exchange_info.get("arguments", {})
            persistent = arguments.get("persistent", False)
            return persistent
        else:
            return False
    
    # Mètode per connectar-se a un chat grupal
    def connect_group_chat(self):
        group_name = input("Introdueix el nom del grup: ")
        
        # Comprovacions inicials
        if group_name in self.group_chats:
            self.logger.error("Ja tens el chat d'aquest grup obert.")
            return
        
        # Comprovar si el client està subscrit al chat grupal
        if group_name in self.subscribed_chats:
            self.logger.success("Estàs subscrit al chat. (rebràs missatges antics)")
            print("Obrint chat...")
            chat = self.subscribed_chats[group_name]
            self.group_chats[group_name] = chat
            threading.Thread(target=chat.open_chat).start()
            return
        
        # Comprovar si ja existeix un grup amb el nom especificat
        try: 
            self.channel.exchange_declare(exchange=group_name, exchange_type="fanout", passive=True)
            self.logger.success("S'ha trobat el grup.")
            persistent = self.is_exchange_persistent(group_name)
        except Exception:
            self.logger.error("No s'ha trobat el grup, el pots crear subscrivint-te.")
            return
            
        # Comprovar si el chat és persistent
        if persistent:
            self.logger.error("No estàs subscrit al chat. (no rebràs missatges antics)")
            
        # Crear i guardar chat grupal
        print("Obrint chat...")
        chat = GroupChat(self, group_name, persistent)
        self.group_chats[group_name] = chat
        threading.Thread(target=chat.open_chat).start()
    
    # Mètode per subscriure's a un chat grupal
    def subscribe_group(self):
        group_name = input("Introdueix el nom del grup: ")
        
        # Comprovacions inicials
        if group_name in self.subscribed_chats:
            self.logger.error("Ja estàs subscrit a aquest chat.")
            return
        
        # Comprovar si ja existeix un grup amb el nom especificat
        try: 
            self.channel.exchange_declare(exchange=group_name, exchange_type="fanout", passive=True)
            self.logger.success("S'ha trobat el grup.")
            persistent = self.is_exchange_persistent(group_name)
        except Exception:
            self.logger.error("No s'ha trobat el grup. Configurant...")
            # Reconnectar a RabbitMQ
            self.connection.close()
            self.connection, self.channel = self.connect_to_rabbit()
            # Demanar si vol persistència
            persistent = False
            while True:
                option = input("Vols que el chat sigui persistent? [S]í [N]o [C]ancel·lar\n").upper()
                match option:
                    case "S":
                        persistent = True
                        break
                    case "N":
                        break
                    case "C":
                        self.logger.success("S'ha cancel·lat la creació del grup.")
                        return
                    case default:
                        self.logger.error("Opció invàlida. Tria'n una de vàlida.")
            # Crear grup
            print("Creant grup...")
            arguments = {
                "persistent": persistent
            }
            self.channel.exchange_declare(exchange=group_name, exchange_type='fanout', arguments=arguments)
            self.logger.success("S'ha creat el chat grupal.")
        
        print("Subscribint...")
        persistent = self.is_exchange_persistent(group_name)
        if persistent:
            chat = GroupChat(self, group_name, persistent)
            self.subscribed_chats[group_name] = chat
            self.logger.success("T'has subscrit al chat grupal.")
        else:
            self.logger.error("No et pots subscriure a un chat no persistent.")
        
    # Mètode per eliminar un chat grupal    
    def close_group_chat(self, group_name):
        if group_name in self.group_chats:
            self.group_chats.pop(group_name)
        
        
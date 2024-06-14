import grpc
import threading
import time
import os
import colorama
import tkinter as tk

# Importar classes gRPC
from proto import chat_pb2
from proto import chat_pb2_grpc

# Importar altres classes
from private_chat import PrivateChat

class Client:
    
    # Constructor
    def __init__(self, username, ip, port, server_stub):
        self.username = username
        self.ip = ip
        self.port = port
        self.server_stub = server_stub
        # Chats privats actius
        self.private_chats = {}
        # Inicialitzar biblioteca de colors per la terminal
        colorama.init()
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
    
    # Mètode per contestar una petició de chat privat
    def connection(self, other_username):
        self.accept = False
        
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
                    chat = PrivateChat(other_username, other_ip, other_port)
                    self.private_chats[other_username] = chat
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
    def connect_chat(self):
        other_username = input("Introdueix el nom d'usuari: ")
        
        # Comprovacions inicials
        if other_username == self.username:
            print(f"{colorama.Back.RED} ✖ {colorama.Back.RESET} No pots iniciar un chat privat amb tu mateix")
            return
        elif other_username in self.private_chats:
            print(f"{colorama.Back.RED} ✖ {colorama.Back.RESET} Ja tens un chat obert amb aquest usuari")
            return
        
        # Obtenir dades de l'altre client
        print("Obtenint dades...")
        response = self.server_stub.GetClientInfo(chat_pb2.GetInfoRequest(username=other_username))
        other_ip = response.ip
        other_port = response.port
        if other_ip == "" and other_port == 0:
            print(f"{colorama.Back.RED} ✖ {colorama.Back.RESET} No s'ha trobat l'usuari")
            return
        else:
            print(f"{colorama.Back.GREEN} ✔ {colorama.Back.RESET} S'ha trobat l'usuari")

        # Sol·licitar chat privat
        print("Sol·licitant chat privat...")
        channel = grpc.insecure_channel(f"{other_ip}:{other_port}")
        other_stub = chat_pb2_grpc.ClientServiceStub(channel)
        response = other_stub.Connection(chat_pb2.ConnectionRequest(username=self.username))
        if not response.accept:
            print(f"{colorama.Back.RED} ✖ {colorama.Back.RESET} L'altre usuari ha denegat la petició")
        else:
            print(f"{colorama.Back.GREEN} ✔ {colorama.Back.RESET} L'altre usuari ha acceptat la petició")
            # Crear i guardar chat privat
            print("Obrint chat...")
            chat = PrivateChat(other_username, other_ip, other_port, other_stub)
            self.private_chats[other_username] = chat
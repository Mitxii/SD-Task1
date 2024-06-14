import grpc
import threading
import time
import tkinter as tk
from tkinter import scrolledtext

# Importar classes gRPC
from proto import chat_pb2
from proto import chat_pb2_grpc

class PrivateChat():
    
    # Constructor
    def __init__(self, client, other_username, other_ip, other_port):
        self.client = client
        self.other_username = other_username
        self.other_ip = other_ip
        self.other_port = other_port
        # Obrir stub
        channel = grpc.insecure_channel(f"{other_ip}:{other_port}")
        self.stub = chat_pb2_grpc.ClientServiceStub(channel)
        # Cua de missatges
        self.messages = []
        # Obrir chat privat en un thread
        threading.Thread(target=self.open_chat).start()
        
    # Mètode per gestionar la desconnexió de l'altre client
    def hearbeat_other(self):
        while True:
            try:
                self.stub.Heartbeat(chat_pb2.Empty())
            except grpc.RpcError:
                self.display_message("EXIT", "left")
                return
            time.sleep(1)
    
    # Mètode per eliminar el chat privat
    def destroy_chat(self):
        # Tancar finestra
        self.chat.destroy()
        # Eliminar de chats actius del client
        self.client.close_chat(self.other_username)
    
    # Mètode per obrir el chat privat
    def open_chat(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Funció per enviar un missatge
        def send_message(ctx=None):
            message = entry_msg.get()
            if message != "":
                # Buidar input
                entry_msg.delete(0, tk.END)
                # Mostrar missatge
                self.display_message(message, "right")
                # Enviar missatge
                self.stub.SendMessage(chat_pb2.Message(username=self.client.username, body=message))
               
        # Configurar finestra de chat privat
        self.chat = tk.Toplevel(self.root)
        self.chat.title(f"[{self.client.username}] {self.other_username}")
        self.chat.geometry("400x500")
        # Frame per als inputs (missatges a enviar)
        self.input_frame = tk.Frame(self.chat)
        self.input_frame.pack(pady=5, padx=10, fill=tk.X, side=tk.BOTTOM)
        send_btn = tk.Button(self.input_frame, text="Enviar", command=send_message, cursor="hand2")
        send_btn.pack(side=tk.RIGHT)
        entry_label = tk.Label(self.input_frame, text="Tu:")
        entry_label.pack(side=tk.LEFT)
        entry_msg = tk.Entry(self.input_frame)
        entry_msg.pack(fill=tk.X, padx=(0, 10))
        entry_msg.bind("<Return>", send_message)
        entry_msg.focus_set()
        # ScrolledText per mostrar els missatges
        self.chat_display = scrolledtext.ScrolledText(self.chat, wrap=tk.WORD, state="disabled")
        self.chat_display.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.chat_display.configure(padx=10, pady=10)

        # Funció per eliminar el chat al tancar-lo
        def close_chat():
            self.stub.SendMessage(chat_pb2.Message(username=self.client.username, body="EXIT"))
            self.destroy_chat()
        self.chat.protocol("WM_DELETE_WINDOW", close_chat)
        
        # Gestionar desconnexió de l'altre client
        threading.Thread(target=self.hearbeat_other).start()

        # Llançar finestra
        self.chat.mainloop()
        
    # Mètode per imprimir un missatge al chat
    def display_message(self, message, alignment):
        # Si el missatge és 'EXIT', vol dir que l'altre client ha tancat el chat o s'ha desconnectat
        if message == "EXIT":
            # Si la posició és a la dreta, vol dir que s'ha enviat (no rebut). Per tant, només es destrueix el chat
            if alignment == "right": 
                self.destroy_chat()
            # Si la posició és a la esquerra, vol dir que s'ha rebut. Per tant, es mostra un missatge per informar
            else:
                # Eliminar tots els elements del frame per als inputs
                for widget in self.input_frame.winfo_children():
                    widget.destroy()
                # Crear un nou missatge per notificar la desconnexió de l'altre client
                tk.Label(self.input_frame, text="** L'altre usuari s'ha desconnectat del chat **").pack()
                self.chat.protocol("WM_DELETE_WINDOW", self.destroy_chat)
        # Si és un altre missatge, s'imprimeix en funció de la posició
        else:
            self.chat_display.config(state="normal")
            self.chat_display.insert(tk.END, f"{message}\n", alignment)
            self.chat_display.tag_configure(alignment, justify=alignment)
            self.chat_display.config(state="disabled")
            self.chat_display.yview(tk.END)
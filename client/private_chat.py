import grpc
import threading
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
    
    # Mètode per eliminar el chat privat
    def destroy_chat(self):
        self.root.destroy()
        self.client.close_chat(self.other_username)
    
    # Mètode per obrir el chat privat
    def open_chat(self):
        
        # Funció per enviar un missatge
        def send_message(ctx=None):
            message = entry_msg.get()
            if message != "":
                self.display_message(message, "right")
                entry_msg.delete(0, tk.END)
                self.stub.SendMessage(chat_pb2.Message(username=self.client.username, body=message))
               
        # Configurar finestra de chat privat
        self.root = tk.Tk()
        self.root.title(f"[{self.client.username}] {self.other_username}")
        self.root.geometry("400x500")
        # Frame per als inputs (missatges a enviar)
        self.input_frame = tk.Frame(self.root)
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
        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state="disabled")
        self.chat_display.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.chat_display.configure(padx=10, pady=10)

        # Funció per eliminar el chat al tancar-lo
        def close_chat():
            self.stub.SendMessage(chat_pb2.Message(username=self.client.username, body="EXIT"))
            self.destroy_chat()
        self.root.protocol("WM_DELETE_WINDOW", close_chat)

        # Llançar finestra
        self.root.mainloop()
        
    # Mètode per imprimir un missatge al chat
    def display_message(self, message, alignment):
        if message == "EXIT":
            # Eliminar tots els elements del frame per als inputs
            for widget in self.input_frame.winfo_children():
                widget.destroy()
            # Crear un nou missatge per notificar la desconnexió de l'altre client
            tk.Label(self.input_frame, text="** L'altre usuari s'ha desconnectat del chat **").pack()
        else:
            self.chat_display.config(state="normal")
            self.chat_display.insert(tk.END, f"{message}\n", alignment)
            self.chat_display.tag_configure(alignment, justify=alignment)
            self.chat_display.config(state="disabled")
            self.chat_display.yview(tk.END)
import threading
import datetime
import pika
import json
import tkinter as tk
from tkinter import scrolledtext

class InsultChat():
    
    # Constructor
    def __init__(self, client):
        self.client = client
        
        # Obrir chat d'insults
        self.open_chat()
    
    # Mètode per connectar-se a RabbitMQ
    def connect_to_rabbit(self):
        credentials = pika.PlainCredentials("user", "password")
        parameters = pika.ConnectionParameters(self.client.server_ip, self.client.server_rabbit_port, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        return connection, channel
    
    # Mètode per eliminar el chat grupal
    def destroy_chat(self):
        # Tancar els canals
        try:
            self.listen_channel.stop_consuming()
        except Exception:
            pass
        try:
            self.listen_connection.close()
        except Exception:
            pass
        try:
            self.connection.close()
        except Exception:
            pass
        
        # Tancar finestra
        self.chat.destroy()

        # Eliminar de chats actius del client
        self.client.insult_chat = False

    # Mètode per consumir la cua i rebre els missatges
    def start_consuming(self):
        self.listen_connection, self.listen_channel = self.connect_to_rabbit()
        
        # Consumir cua
        self.listen_channel.basic_consume(queue="insults", on_message_callback=self.receive_message)
        try:
            self.listen_channel.start_consuming()
        except Exception:
            pass
        
    # Mètode per obrir el chat grupal
    def open_chat(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Obrir connexió
        self.connection, self.channel = self.connect_to_rabbit()
        
        # Temps de l'últim missatge
        self.last = "00:00"
        
        # Funció per enviar un missatge
        def send_message(ctx=None):
            # Obtenir hora
            now = datetime.datetime.now()
            time = now.strftime("%H:%M")
            # Obtenir missatge
            message = entry_msg.get()
            if message != "":
                # Buidar input
                entry_msg.delete(0, tk.END)
                # Mostrar missatge
                self.display_message(f"{message} [👤]", time, "right")
                # Codificar missatge en json
                message = {
                    "username": self.client.username,
                    "message": message,
                    "timestamp": time
                }
                message = json.dumps(message)
                # Enviar missatge
                self.channel.basic_publish(exchange="", routing_key="insults", body=message)
        
        # Configurar finestra de chat grupal
        self.chat = tk.Toplevel(self.root)
        self.chat.title(f"[{self.client.username}] 🤬 Insults")
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
            # Desactivar inpunts mentre es tanquen els canals
            self.chat.title("Parant...")
            for widget in self.input_frame.winfo_children():
                widget.destroy()
                # Destruir chat
            self.destroy_chat()
        self.chat.protocol("WM_DELETE_WINDOW", close_chat)
            
        # Començar a consumir missatges
        threading.Thread(target=self.start_consuming).start()
        
        # Llançar finestra
        self.chat.mainloop()
        
    # Mètode per imprimir un missatge al chat
    def display_message(self, message, time, alignment):
        self.chat_display.config(state="normal")
        # Imprimir temps
        if time != self.last:
            self.chat_display.insert(tk.END, f"{time}\n", f"time")
            self.last = time
        self.chat_display.tag_configure("time", font=("Helvetica", 8), justify="center")
        # Imprimir missatge
        self.chat_display.insert(tk.END, f"{message}\n", alignment)
        self.chat_display.tag_configure(alignment, justify=alignment)
        self.chat_display.config(state="disabled")
        self.chat_display.yview(tk.END)
    
    # Mètode per rebre i processar els missatges
    def receive_message(self, ch, method, properties, body):
        body = json.loads(body)
        username = body.get("username")
        # Evitar que consumeixi el missatge el client que l'ha enviat
        if username == self.client.username:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        else:
            text = body.get("message")
            time = body.get("timestamp")
            message = f"[🤡] {text}"
            self.display_message(message, time, "left")
            ch.basic_ack(delivery_tag=method.delivery_tag)
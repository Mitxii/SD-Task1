import threading
import datetime
import pika
import json
import tkinter as tk
from tkinter import scrolledtext

class GroupChat():
    
    # Constructor
    def __init__(self, client, group_name, persistent):
        self.client = client
        self.group_name = group_name
        # Modificar la persistència dels missatges en funció de la del exchange
        self.persistent = 1
        if persistent: self.persistent = 2
        
        # Configurar cua del client
        self.queue_name = ""
        self.configure_queue()
        
        # Obrir chat grupal en un thread
        #threading.Thread(target=self.open_chat).start()
    
    # Mètode per connectar-se a RabbitMQ
    def connect_to_rabbit(self):
        credentials = pika.PlainCredentials("user", "password")
        parameters = pika.ConnectionParameters(self.client.server_ip, self.client.server_rabbit_port, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        return connection, channel
    
    def configure_queue(self):
        connection, channel = self.connect_to_rabbit()
        result = channel.queue_declare(queue="", durable=True)
        self.queue_name = result.method.queue
        channel.queue_bind(exchange=self.group_name, queue=self.queue_name)
        connection.close()
    
    # Mètode per eliminar el chat grupal
    def destroy_chat(self):
        # Tancar els canals
        try:
            self.listen_channel.stop_consuming()
        except Exception:
            pass
        try:
            self.listen_channel.close()
        except Exception:
            pass
        try:
            self.channel.close()
        except Exception:
            pass
        # Tancar finestra
        self.chat.destroy()
        
        # Eliminar de chats actius del client
        self.client.close_group_chat(self.group_name)

    # Mètode per obtenir i mostrar missatges antics
    def fetch_old_messages(self):
        # Obrir connexió
        channel = self.connect_to_rabbit()
        result = channel.queue_declare(queue=self.group_name, durable=True)
        queue_name = result.method.queue

        # Obtenir els missatges
        messages = []
        method_frame, header_frame, body = channel.basic_get(queue_name)
        while method_frame:
            messages.append(json.loads(body))
            method_frame, header_frame, body = channel.basic_get(queue_name)
        
        # Tancar el canal
        channel.close()

        # Mostrar missatges
        for message in messages:
            if message["username"] == self.client.username:
                self.display_message(f"{message['message']} [👤]", message['timestamp'], "right")
            else:
                self.display_message(f"[{message['username']}] {message['message']}", message['timestamp'], "left")

    # Mètode per consumir la cua i rebre els missatges
    def start_consuming(self):
        self.listen_channel = self.connect_to_rabbit()
        result = self.listen_channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue
        self.listen_channel.queue_bind(exchange=self.group_name, queue=queue_name)
        self.listen_channel.basic_consume(queue=queue_name, on_message_callback=self.receive_message, auto_ack=True)
        try:
            self.listen_channel.start_consuming()
        except Exception:
            pass
        
    # Mètode per obrir el chat grupal
    def open_chat(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Obrir connexió
        self.channel = self.connect_to_rabbit()
        
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
                self.channel.basic_publish(exchange=self.group_name, routing_key="", body=message, properties=pika.BasicProperties(delivery_mode=self.persistent))
        
        # Configurar finestra de chat grupal
        self.chat = tk.Toplevel(self.root)
        self.chat.title(f"[{self.client.username}] 👥 {self.group_name}")
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
        
        # Si és un chat persistent, mostrar missatgs antics
        if self.persistent == 2:
            self.chat.after(0, self.fetch_old_messages)
            
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
        # Evitar duplicar la impressió al client que envia
        if username != self.client.username:
            text = body.get("message")
            time = body.get("timestamp")
            message = f"[{username}] {text}"
            self.display_message(message, time, "left")
import threading
import datetime
import tkinter as tk
from tkinter import scrolledtext

class GroupChat():
    
    # Constructor
    def __init__(self, client, group_name, channel):
        self.client = client
        self.group_name = group_name
        self.channel = channel
        # Obrir chat grupal en un thread
        threading.Thread(target=self.open_chat).start()
        
    # Mètode per eliminar el chat grupal
    def destroy_chat(self):
        # Tancar finestra
        self.chat.destroy()
        # Eliminar de chats actius del client
        self.client.close_group_chat(self.group_name)

    def open_chat(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
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
                self.display_message(message, time, "right")
                # Enviar missatge
                
        
        # Configurar finestra de chat grupal
        self.chat = tk.Toplevel(self.root)
        self.chat.title(f"[{self.client.username}] {self.group_name}")
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
            self.destroy_chat()
        self.chat.protocol("WM_DELETE_WINDOW", close_chat)
        
        # Llançar finestra
        self.chat.mainloop()
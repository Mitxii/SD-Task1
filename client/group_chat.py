import threading
import tkinter as tk

class GroupChat():
    
    # Constructor
    def __init__(self, client, group_name, channel):
        self.client = client
        self.group_name = group_name
        self.channel = channel
        # Obrir chat grupal en un thread
        threading.Thread(target=self.open_chat).start()
        
    def open_chat(self):
        self.root = tk.Tk()
        
        # Configurar finestra de chat grupal
        self.chat = tk.Toplevel(self.root)
        self.chat.title(f"[{self.client.username}] {self.group_name}")
        self.chat.geometry("400x500")
        
        # Llançar finestra
        self.chat.mainloop()
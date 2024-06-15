import colorama
from datetime import datetime

# Inicialitzar biblioteca de colors per la terminal
colorama.init()

class ServerLog:
    
    # Constructor
    def __init__(self, source):
        self.source = source.__class__.__name__
        match self.source:
            case "MessageBroker":
                self.back_color = colorama.Back.MAGENTA
            case "NameServer":
                self.back_color = colorama.Back.YELLOW
            case default:
                self.back_color = colorama.Back.WHITE + colorama.Fore.BLACK
        self.reset = colorama.Back.RESET + colorama.Fore.RESET
    
    # Mètode per obtenir el temps (hora:minuts)
    def get_timestamp(ctx=False):
        return datetime.now().strftime("%H:%M")
        
    # Mètode per imprimir un missatge de log
    def log(self, log):
        timestamp = self.get_timestamp()
        print(f"{timestamp} {self.back_color} {self.source} {self.reset} - {log}")
          
    # Mètode per imprimir un missatge d'error  
    def error(self, error):
        timestamp = self.get_timestamp()
        print(f"{timestamp} {self.back_color} {self.source} {self.reset + colorama.Fore.RED} ✖ {self.reset + error}")
    
    # Mètode per imprimir un missatge d'èxit  
    def success(self, succ):
        timestamp = self.get_timestamp()
        print(f"{timestamp} {self.back_color} {self.source} {self.reset + colorama.Fore.GREEN} ✔ {self.reset + succ}")
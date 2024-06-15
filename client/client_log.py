import colorama

# Inicialitzar biblioteca de colors per la terminal
colorama.init()

class ClientLog:
          
    # Mètode per imprimir un missatge d'error  
    def error(self, error):
        print(f"{colorama.Fore.RED} ✖ {colorama.Fore.RESET + error}")
    
    # Mètode per imprimir un missatge d'èxit  
    def success(self, succ):
        print(f"{colorama.Fore.GREEN} ✔ {colorama.Fore.RESET + succ}")
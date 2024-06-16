## Aplicació de Xat Online

# Descripció del Projecte
Aquest projecte és una aplicació de xat online desenvolupada com a part de l'assignatura de Sistemes Distribuïts de la Universitat Rovira i Virgili, curs 2023/2024. L'objectiu és implementar diversos patrons de comunicació en sistemes distribuïts mitjançant una aplicació de xat que inclou xats privats i grupals, subscripcions a grups de xat, descobriment de xats actius i un canal d'insults. El servidor utilitza Redis per a la gestió de noms i RabbitMQ per a la gestió de missatges.

# Funcionalitats
Xats Privats: Comunicació directa entre dos clients.
Xats Grupals: Comunicació entre múltiples clients amb possible subscripció.
Descobriment de Xats: Llista dels xats actius en el moment de la sol·licitud.
Canal d'Insults: Enviar un missatge d'insult a un client connectat de manera aleatòria.

# Requisits del Sistema
Python 3.11+
Redis
RabbitMQ
Docker

# Instal·lació
1. Clonar el repositori
    git clone https://github.com/Mitxii/SD-Task1.git
2. Si dona problemes de mòduls, prova a crear de nou el entorn virtual
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

# Ús
1. Llançar el servidor central
    ./start-server.sh
2. Llançar tants clients com vulguis
    ./start-client.sh

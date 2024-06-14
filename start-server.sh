#!/bin/bash

BACK_RED="\033[41;37m"
RESET="\033[0m"

# Comprovar si ja hi ha un servidor en marxa
if ps aux | grep -v grep | grep server.py > /dev/null
then
    echo -e "${BACK_RED} ✖ ${RESET} Ja hi ha un servidor en marxa."
    exit 1
fi

# Obtenir port del servidor
port=50000
while true
do 
    netstat -tuln | grep $port &> /dev/null
    if [ $? -eq 0 ]; then
        echo -e "${BACK_RED} ✖ ${RESET} El port $port ja està ocupat."
        port=$((port+1))
    else
        break
    fi
done

# Obtenir IP del servidor
ip=$(hostname -I | awk '{print $1}')

# Guardar variables al fitxer config
echo "server:" > config.yaml
echo "  ip: $ip" >> config.yaml
echo "  grpc_port: $port" >> config.yaml
echo "  rabbit_port: 5672" >> config.yaml

# Agregar directori 'proto' al sys.path
PROTO_ABS_DIR=$(realpath "./proto")
export PYTHONPATH="$PROTO_ABS_DIR:$PYTHONPATH"

# Funció per comprovar si una comanda existeix
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Instal·lar Docker si no està instal·lat
if ! command_exists docker; then
    echo "Docker no està instal·lat. Instal·lant Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    sudo usermod -aG docker $USER
    echo "Docker s'ha instal·lat correctament. Si us plau, tanca la sessió i torna a iniciar-la per aplicar els canvis."
    exit 1
fi

# Instal·lar Docker Compose si no està instal·lat
if ! command_exists docker-compose; then
    echo "Docker Compose no està instal·lat. Instal·lant Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -Po '(?<="tag_name": ")[^"]*')/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose s'ha instal·lat correctament."
fi

# Crear directori per guardar les dades de RabbitMQ
mkdir -p rabbitmq_data

# Aturar contenidor RabbitMQ en cas de que estigui encés
echo "Reiniciant RabbitMQ..."
docker stop rabbitmq > /dev/null 2>&1

# Iniciar RabbitMQ en un contenidor Docker
docker-compose up -d

# Canviar entorn python
source venv/bin/activate

# Engegar servidor
gnome-terminal --title="SERVER" -- python3 server/server.py --port $port  2> /dev/null
#python3 server/server.py --port $port
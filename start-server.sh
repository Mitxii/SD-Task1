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

# Agregar directori 'proto' al sys.path
PROTO_ABS_DIR=$(realpath "./proto")
export PYTHONPATH="$PROTO_ABS_DIR:$PYTHONPATH"

# Canviar entorn python
source venv/bin/activate

# Engegar servidor
gnome-terminal --title="SERVER" -- python3 server/server.py --port $port  2> /dev/null
#python3 server/server.py --port $port
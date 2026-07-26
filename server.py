import socket
import subprocess
import platform
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Permitir peticiones desde tu archivo HTML sin problemas de CORS
CORS(app) 

def enviar_wol(mac, ip, puerto=9):
    try:
        # Limpiar la MAC (remover guiones o dos puntos)
        mac_limpia = mac.replace("-", "").replace(":", "")
        if len(mac_limpia) != 12:
            return False, "Formato de MAC inválido."
            
        # Construir el paquete mágico
        paquete = bytes.fromhex("FF" * 6 + mac_limpia * 16)
        
        # Enviar vía UDP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(paquete, (ip, puerto))
            
        return True, "Enviado"
    except Exception as e:
        return False, str(e)

def verificar_estado(ip):
    # Detectar el sistema operativo del servidor para usar el comando ping correcto
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    # Solo 1 paquete, tiempo de espera 1 segundo
    comando = ['ping', param, '1', '-w', '1000' if platform.system().lower() == 'windows' else '1', ip]
    
    try:
        # Ejecuta el ping de forma silenciosa
        resultado = subprocess.call(comando, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        # returncode 0 significa que el PC respondió al ping (está encendido)
        return resultado == 0
    except:
        return False

@app.route('/api/wake', methods=['POST'])
def api_wake():
    data = request.json
    mac = data.get('mac')
    ip = data.get('ip')
    
    if not mac or not ip:
        return jsonify({"success": False, "error": "Faltan datos"}), 400
        
    exito, mensaje = enviar_wol(mac, ip)
    
    if exito:
        return jsonify({"success": True, "message": mensaje})
    else:
        return jsonify({"success": False, "error": mensaje}), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    ip = request.args.get('ip')
    if not ip:
        return jsonify({"online": False}), 400
        
    estado = verificar_estado(ip)
    return jsonify({"online": estado})

@app.route('/', methods=['GET'])
def home():
    return "El servidor Wake-on-LAN está funcionando correctamente en la nube 🚀"

if __name__ == '__main__':
    print("Iniciando Servidor de Wake-on-LAN en http://127.0.0.1:5000")
    print("Manten esta ventana abierta mientras usas la web.")
    # Iniciar servidor en el puerto 5000 (accesible en la red local si cambias a host='0.0.0.0')
    app.run(host='0.0.0.0', port=5000, debug=False)
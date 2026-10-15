from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import socket
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)

# Inicialização segura do Firebase Firestore
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Conectado ao Firebase Firestore com sucesso!")
except Exception as e:
    print("Aviso: Firebase Admin não inicializado. Coloque o serviceAccountKey.json na pasta. Erro:", e)
    db = None

PC_MAC_ADDRESS = "3C:7C:3F:7B:E9:83"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "online", "mensagem": "Servidor Jarvis rodando com sucesso!"})

@app.route('/pc/ligar', methods=['POST'])
def ligar_pc():
    try:
        mac_limpo = PC_MAC_ADDRESS.replace('-', '').replace(':', '')
        data = bytes.fromhex('FF' * 6 + mac_limpo * 16)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(data, ('255.255.255.255', 9))
        return jsonify({"status": "sucesso", "mensagem": "Pacote Wake-on-LAN enviado!"})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/pc/desligar', methods=['POST'])
def desligar_pc():
    try:
        os.system("shutdown /s /t 1")
        return jsonify({"status": "sucesso", "mensagem": "Desligando o computador..."})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/pc/apps', methods=['GET'])
def listar_apps():
    apps_comuns = [
        {"nome": "Google Chrome", "comando": "chrome"},
        {"nome": "Spotify", "comando": "spotify"},
        {"nome": "Bloco de Notas", "comando": "notepad"},
        {"nome": "Calculadora", "comando": "calc"},
        {"nome": "Explorador de Arquivos", "comando": "explorer"},
        {"nome": "Prompt de Comando", "comando": "cmd"},
        {"nome": "Visual Studio Code", "comando": "code"}
    ]
    return jsonify(apps_comuns)

@app.route('/pc/abrir', methods=['POST'])
def abrir_app():
    dados = request.get_json() or {}
    app_nome = dados.get("app", "")
    try:
        os.system(f"start {app_nome}")
        return jsonify({"status": "sucesso", "mensagem": f"Aplicativo '{app_nome}' aberto!"})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
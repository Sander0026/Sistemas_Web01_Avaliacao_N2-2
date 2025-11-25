import sys
import os
import threading
from flask import Flask, request, jsonify
from tinydb import TinyDB, Query
from queue import Queue  # Usamos a Queue padrão aqui
from multiprocessing.managers import BaseManager

# --- Configuração de Path ---
# Adiciona o diretório raiz do projeto ao sys.path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(project_root)
# --- Fim da Configuração de Path ---


try:
    # Corrigido "lambidas" para "lambdas"
    from src.lambdas.lambda_validador import validar_ordem
    
    # Corrigido "criar_bancos_tinydb" para "inicializar_bancos"
    from database.init_db import inicializar_bancos
    
    # Importa os caminhos dos bancos
    from database.db_config import DB_TRANSACOES_PATH, DB_USUARIOS_PATH
    
    # Importa as definições do SERVIDOR DE FILAS
    from filas.queue_manager import (
        QUEUE_MANAGER_PORT, 
        QUEUE_MANAGER_AUTHKEY, 
        FILA_ORDENS, 
        FILA_PUSH, 
        FILA_EMAIL
    )
except ImportError as e:
    print(f"Erro fatal de importação no app.py: {e}")
    print("Verifique os nomes dos arquivos e funções (ex: 'lambdas', 'inicializar_bancos')")
    sys.exit(1)

# --- Inicialização ---
app = Flask(__name__)

# 1. CRIAMOS AS 3 INSTÂNCIAS DE FILA
fila_ordens_validas = Queue()
fila_notificacao_push = Queue()
fila_notificacao_email = Queue()

# 2. FUNÇÃO PARA INICIAR O SERVIDOR DE FILAS (MÉTODO B)
def iniciar_servidor_filas():
    """
    Cria e expõe as filas na rede (localhost) para os workers se conectarem.
    """
    print(f"[SERVIDOR_FILAS] Iniciando o Manager na porta {QUEUE_MANAGER_PORT}...")
    
    # Registra cada fila com seu "nome" (ramal)
    BaseManager.register(FILA_ORDENS, callable=lambda: fila_ordens_validas)
    BaseManager.register(FILA_PUSH, callable=lambda: fila_notificacao_push)
    BaseManager.register(FILA_EMAIL, callable=lambda: fila_notificacao_email)
    
    # Inicia o servidor
    manager_servidor = BaseManager(
        address=('', QUEUE_MANAGER_PORT), 
        authkey=QUEUE_MANAGER_AUTHKEY
    )
    
    servidor = manager_servidor.get_server()
    print("[SERVIDOR_FILAS] 🚀 Servidor de filas rodando!")
    servidor.serve_forever()

# --- Endpoints da API (Gateway) ---

@app.route('/comprar', methods=['POST'])
def comprar_acao():
    ordem = request.get_json()
    if not ordem:
        return jsonify({"erro": "Corpo da requisição não é um JSON válido"}), 400

    # 1. Validação (Lambda 1)
    if not validar_ordem(ordem):
        return jsonify({"erro": "Dados da ordem inválidos (ex: user_id, ticker, quantidade)"}), 400

    # 2. Coloca a ordem na fila (que o worker_ordens vai pegar)
    try:
        fila_ordens_validas.put(ordem)
    except Exception as e:
        print(f"Erro ao colocar na fila: {e}")
        return jsonify({"erro": "Falha ao enfileirar ordem"}), 500

    # 3. Responde 202 Accepted
    return jsonify({"mensagem": "Ordem recebida e em processamento"}), 202

@app.route('/transacoes/<int:user_id>', methods=['GET'])
def get_transacoes(user_id):
    # Endpoint Síncrono
    try:
        db_transacoes = TinyDB(DB_TRANSACOES_PATH)
        Transacao = Query()
        transacoes_usuario = db_transacoes.search(Transacao.user_id == user_id)
        db_transacoes.close()
        return jsonify(transacoes_usuario)
    except Exception as e:
        return jsonify({"erro": f"Erro ao ler banco: {e}"}), 500

@app.route('/usuarios/<int:user_id>', methods=['GET'])
def get_usuario(user_id):
    # Endpoint Síncrono
    try:
        db_usuarios = TinyDB(DB_USUARIOS_PATH)
        User = Query()
        usuario = db_usuarios.get(User.user_id == user_id)
        db_usuarios.close()
        if usuario:
            return jsonify(usuario)
        return jsonify({"erro": "Usuário não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": f"Erro ao ler banco: {e}"}), 500

# --- Bloco de Inicialização ---

if __name__ == '__main__':
    # 1. Cria os bancos de dados
    print("[SISTEMA] Inicializando bancos de dados...")
    inicializar_bancos()

    # 2. Inicia o SERVIDOR DE FILAS em uma Thread separada
    # (daemon=True faz ela fechar junto com o app)
    print("[SISTEMA] Iniciando Servidor de Filas em background...")
    thread_servidor = threading.Thread(target=iniciar_servidor_filas, daemon=True)
    thread_servidor.start()

    # 3. Inicia o SERVIDOR FLASK (na thread principal)
    print(f"[SISTEMA] Iniciando API Flask na porta 5000...")
    app.run(port=5000, host='0.0.0.0', debug=False)
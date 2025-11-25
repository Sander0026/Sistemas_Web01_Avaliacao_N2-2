import sys
import os
import time
from multiprocessing.managers import BaseManager

# --- Configuração de Path ---
# Adiciona o diretório raiz do projeto ao path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
# --- Fim da Configuração de Path ---

# Importa a lambda específica de notificação push e as configs de fila
try:
    from src.lambdas import lambda_notificador
    
    # Importa as configs de conexão E o nome da fila PUSH
    from filas.queue_manager import (
        QUEUE_MANAGER_PORT, 
        QUEUE_MANAGER_AUTHKEY, 
        FILA_PUSH  # Atenção: Fila diferente!
    )
except ImportError:
    print("Erro: Não foi possível encontrar os módulos 'src'.")
    print("Verifique a estrutura de pastas e o 'queue_manager.py'.")
    sys.exit(1)


def conectar_ao_gerenciador_de_filas():
    """
    Tenta se conectar ao Manager de filas.
    Este código é IDÊNTICO ao do 'worker_ordens.py'.
    """
    print("[WORKER_PUSH] Conectando ao servidor de filas (localhost:50001)...")
    
    # Registra o nome da fila que este worker precisa
    BaseManager.register(FILA_PUSH) 
    
    manager_cliente = BaseManager(
        address=('127.0.0.1', QUEUE_MANAGER_PORT), 
        authkey=QUEUE_MANAGER_AUTHKEY
    )
    
    while True:
        try:
            manager_cliente.connect()
            print("[WORKER_PUSH] 🚀 Conectado ao servidor de filas!")
            return manager_cliente
        except ConnectionRefusedError:
            print("[WORKER_PUSH] Conexão recusada. Tentando novamente em 5s...")
            time.sleep(5)

def iniciar_worker():
    """
    Função principal do worker. Fica em loop infinito escutando a fila de PUSH.
    """
    manager = conectar_ao_gerenciador_de_filas()
    
    # Pega o objeto da fila 'fila_notificacao_push'
    fila_push = getattr(manager, FILA_PUSH)() 
    
    print(f"[WORKER_PUSH] Aguardando notificações na fila '{FILA_PUSH}'...")

    while True:
        try:
            # .get() bloqueia e "dorme" até uma mensagem chegar
            mensagem = fila_push.get()
            
            print(f"\n[WORKER_PUSH] 📥 Nova notificação PUSH recebida: {mensagem}")
            print(f"[WORKER_PUSH] ⚙️ Iniciando 'lambda_notificador'...")
            
            # Executa a Lambda de notificação (que apenas simula com um print)
            lambda_notificador.notificar(mensagem)
            
            print(f"[WORKER_PUSH] ✅ Notificação PUSH enviada.")
            print(f"[WORKER_PUSH] Aguardando novas notificações...")

        except (KeyboardInterrupt, SystemExit):
            print("[WORKER_PUSH] Desligando...")
            break
        except Exception as e:
            print(f"[WORKER_PUSH] ❌ ERRO ao processar notificação {mensagem}: {e}")

if __name__ == "__main__":
    iniciar_worker()
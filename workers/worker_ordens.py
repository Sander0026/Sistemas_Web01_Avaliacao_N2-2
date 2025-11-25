import sys
import os
import time
from multiprocessing.managers import BaseManager

# --- Configuração de Path ---
# Adiciona o diretório raiz do projeto (projeto_carteira_aws) ao path
# Isso permite que este script encontre os módulos em 'src'
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
# --- Fim da Configuração de Path ---

# Importa as lambdas e as configurações de fila agora que o path está correto
try:
    # A lambda que este worker irá executar
    from src.lambdas import lambda_processador_preco 
    
    # As configurações de conexão com o servidor de filas
    from filas.queue_manager import (
        QUEUE_MANAGER_PORT, 
        QUEUE_MANAGER_AUTHKEY, 
        FILA_ORDENS
    )
except ImportError:
    print("Erro: Não foi possível encontrar os módulos 'src'.")
    print("Verifique a estrutura de pastas e se o 'queue_manager.py' existe.")
    sys.exit(1)


def conectar_ao_gerenciador_de_filas():
    """
    Tenta se conectar ao Manager de filas que está rodando (iniciado pela api.py).
    Este worker é um CLIENTE do serviço de filas.
    """
    print("[WORKER_ORDENS] Conectando ao servidor de filas (localhost:50001)...")
    
    # Registra os *nomes* das filas que este worker precisa acessar
    # O nome deve ser o mesmo que foi registrado no servidor (api.py)
    BaseManager.register(FILA_ORDENS)
    
    # Aponta para o endereço do servidor de filas
    manager_cliente = BaseManager(
        address=('127.0.0.1', QUEUE_MANAGER_PORT), 
        authkey=QUEUE_MANAGER_AUTHKEY
    )
    
    # Tenta conectar em loop (caso o worker inicie antes da api)
    while True:
        try:
            manager_cliente.connect()
            print("[WORKER_ORDENS] 🚀 Conectado ao servidor de filas!")
            return manager_cliente
        except ConnectionRefusedError:
            print("[WORKER_ORDENS] Conexão recusada. Tentando novamente em 5s...")
            time.sleep(5)

def iniciar_worker():
    """
    Função principal do worker. Fica em loop infinito escutando a fila.
    """
    # 1. Conecta ao Manager e obtém o objeto da fila
    manager = conectar_ao_gerenciador_de_filas()
    
    # Pega o objeto da fila 'fila_ordens_validas' usando o nome que registramos
    fila_ordens = getattr(manager, FILA_ORDENS)() 
    
    print(f"[WORKER_ORDENS] Aguardando ordens na fila '{FILA_ORDENS}'...")

    # 2. Loop infinito para processar as ordens
    while True:
        try:
            # .get() é bloqueante: o script "dorme" aqui até uma ordem chegar
            ordem = fila_ordens.get()
            
            print(f"\n[WORKER_ORDENS] 📥 Nova ordem recebida: {ordem}")
            print(f"[WORKER_ORDENS] ⚙️ Iniciando 'lambda_processador_preco'...")
            
            # 3. Executa a Lógica (A Lambda)
            # Esta é a parte principal: chama a função de negócio
            # A 'lambda_processador_preco' fará todo o trabalho:
            # - Chamar o Yahoo Finance
            # - Salvar nos bancos de dados
            # - Chamar a 'lambda_consolidador' para continuar o fluxo
            lambda_processador_preco.processar(ordem)
            
            print(f"[WORKER_ORDENS] ✅ Ordem {ordem.get('ticker')} processada com sucesso.")
            print(f"[WORKER_ORDENS] Aguardando novas ordens...")

        except (KeyboardInterrupt, SystemExit):
            print("[WORKER_ORDENS] Desligando...")
            break
        except Exception as e:
            # Em um projeto real, aqui colocaria a ordem em uma "Dead Letter Queue" (DLQ)
            print(f"[WORKER_ORDENS] ❌ ERRO CRÍTICO ao processar ordem {ordem}: {e}")
            # Continua o loop para a próxima ordem

if __name__ == "__main__":
    iniciar_worker()
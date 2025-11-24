import sys
import os
from tinydb import TinyDB, Query
from multiprocessing.managers import BaseManager

# --- Configuração de Path ---
# Sobe dois níveis (de src/lambdas) para o diretório raiz do projeto
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.append(project_root)

# Importa os caminhos dos 3 BANCOS e as configs das 2 FILAS DE NOTIFICAÇÃO
try:
    from database.db_config import (
        DB_TRANSACOES_PATH, 
        DB_COTACOES_PATH, 
        DB_USUARIOS_PATH
    )
    from filas.queue_manager import (
        QUEUE_MANAGER_PORT, 
        QUEUE_MANAGER_AUTHKEY, 
        FILA_PUSH, 
        FILA_EMAIL
    )
except ImportError:
    print("Erro: Não foi possível encontrar 'db_config.py' ou 'queue_manager.py'.")
    sys.exit(1)

# Cache de Conexão com Filas
# Como esta lambda é chamada por outra (não é um worker),
# não queremos reconectar ao Manager toda vez.
_queue_manager_client = None
_fila_push = None
_fila_email = None

def _conectar_filas_notificacao():
    """
    Conecta (ou reutiliza a conexão) ao Manager para ENVIAR mensagens.
    """
    global _queue_manager_client, _fila_push, _fila_email
    
    # Se já conectamos antes, apenas retorna as filas
    if _queue_manager_client:
        return _fila_push, _fila_email

    try:
        print("[LAMBDA_CONSOLIDADOR] Conectando ao servidor de filas (para enviar notificações)...")
        BaseManager.register(FILA_PUSH)
        BaseManager.register(FILA_EMAIL)
        
        manager = BaseManager(
            address=('127.0.0.1', QUEUE_MANAGER_PORT), 
            authkey=QUEUE_MANAGER_AUTHKEY
        )
        manager.connect()
        
        # Salva as conexões no cache global
        _queue_manager_client = manager
        _fila_push = getattr(manager, FILA_PUSH)()
        _fila_email = getattr(manager, FILA_EMAIL)()
        
        print("[LAMBDA_CONSOLIDADOR] Conectado às filas de notificação.")
        return _fila_push, _fila_email
        
    except Exception as e:
        print(f"[LAMBDA_CONSOLIDADOR] ERRO FATAL ao conectar nas filas de notificação: {e}")
        return None, None

# Função Principal (Chamada pela Lambda Anterior) 

def consolidar(user_id):
    """
    Função principal desta lambda.
    Recebe um user_id, recalcula o valor total da carteira desse usuário
    e dispara as notificações.
    """
    print(f"[LAMBDA_CONSOLIDADOR] ⚙️ Iniciando consolidação para user_id: {user_id}")
    
    try:
        # Conectar aos Bancos TinyDB
        db_transacoes = TinyDB(DB_TRANSACOES_PATH)
        db_cotacoes = TinyDB(DB_COTACOES_PATH)
        db_usuarios = TinyDB(DB_USUARIOS_PATH)
        
        User = Query()
        Transacao = Query()
        Cotacao = Query()

        # Buscar todas as transações do usuário
        transacoes_usuario = db_transacoes.search(Transacao.user_id == user_id)
        
        if not transacoes_usuario:
            print(f"[LAMBDA_CONSOLIDADOR] Nenhuma transação encontrada para user_id: {user_id}")
            return

        # Agregar o portfólio (somar todas as quantidades por ticker)
        # Ex: 10 PETR4 + 5 PETR4 = 15 PETR4
        portfolio_agregado = {}
        for t in transacoes_usuario:
            ticker = t['ticker']
            qtd = t['quantidade']
            portfolio_agregado[ticker] = portfolio_agregado.get(ticker, 0) + qtd
        
        valor_total_carteira = 0.0

        # Cruzar com as cotações atuais para calcular o valor total
        for ticker, quantidade_total in portfolio_agregado.items():
            # Busca o preço mais recente que salvamos no BD de cotações
            cotacao_atual_doc = db_cotacoes.get(Cotacao.ticker == ticker)
            
            if cotacao_atual_doc:
                preco_atual = cotacao_atual_doc['ultimo_preco']
                valor_total_carteira += preco_atual * quantidade_total
            else:
                # Isso pode acontecer se o worker falhou em buscar a cotação
                print(f"[LAMBDA_CONSOLIDADOR] Aviso: Cotação para {ticker} não encontrada no BD. Ignorando do cálculo.")

        # Atualizar o 'banco_usuarios' com o novo valor total
        db_usuarios.update(
            {'valor_total_carteira': round(valor_total_carteira, 2)},
            User.user_id == user_id
        )
        print(f"[LAMBDA_CONSOLIDADOR] ✅ 'banco_usuarios' atualizado. Novo valor total para user_id {user_id}: R$ {valor_total_carteira:.2f}")

        # Disparar o "Fan-Out" (Enviar para as duas filas de notificação)
        fila_push, fila_email = _conectar_filas_notificacao()
        
        if fila_push and fila_email:
            msg_push = {
                'user_id': user_id, 
                'mensagem': f"Sua carteira foi atualizada: R$ {valor_total_carteira:.2f}"
            }
            msg_email = {
                'user_id': user_id, 
                'assunto': 'Atualização do seu Portfólio', 
                'valor': f"R$ {valor_total_carteira:.2f}"
            }
            
            fila_push.put(msg_push)
            fila_email.put(msg_email)
            
            print(f"[LAMBDA_CONSOLIDADOR] 📤 Mensagens de PUSH e EMAIL enfileiradas.")
        
        print(f"[LAMBDA_CONSOLIDADOR] Consolidação concluída para user_id: {user_id}")

    except Exception as e:
        print(f"[LAMBDA_CONSOLIDADOR] ❌ ERRO CRÍTICO ao consolidar para user_id {user_id}: {e}")
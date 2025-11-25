import sys
import os
import yfinance as yf
from tinydb import TinyDB, Query
from datetime import datetime

# --- Configuração de Path ---
# Sobe dois níveis (de src/lambdas) para o diretório raiz do projeto
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.append(project_root)
# --- Fim da Configuração de Path ---

# Importa os caminhos dos bancos e a PRÓXIMA lambda
try:
    from database.db_config import DB_TRANSACOES_PATH, DB_COTACOES_PATH
    # Esta é a "continuação" do fluxo, que chamaremos no final
    from src.lambdas import lambda_consolidador 
except ImportError:
    print("Erro: Não foi possível encontrar 'db_config.py' ou 'lambda_consolidador'.")
    sys.exit(1)


def _buscar_preco_ativo(ticker):
    """
    Função interna para buscar o preço mais recente de um ativo.
    Adiciona ".SA" para ações da B3.
    """
    try:
        ticker_b3 = f"{ticker.upper()}.SA"
        ativo = yf.Ticker(ticker_b3)
        # 'fast_info' é mais rápido para o preço atual
        preco = ativo.fast_info.get('last_price') 
        
        if not preco:
            # Fallback se 'last_price' não estiver disponível
            preco = ativo.history(period="1d")['Close'].iloc[-1]
            
        print(f"[LAMBDA_PROC_PRECO] Preço de {ticker_b3} obtido: {preco}")
        return preco
    except Exception as e:
        print(f"[LAMBDA_PROC_PRECO] ERRO ao buscar preço para {ticker}: {e}")
        return None

def _atualizar_cotacao_atual(ticker, preco):
    """
    Atualiza (ou insere) o preço mais recente do ativo no banco de cotações.
    Usa o padrão "upsert" do TinyDB.
    """
    db_cotacoes = TinyDB(DB_COTACOES_PATH)
    Cotacao = Query()
    db_cotacoes.upsert(
        {
            'ticker': ticker.upper(), 
            'ultimo_preco': round(preco, 2), 
            'timestamp_update': str(datetime.now())
        },
        Cotacao.ticker == ticker.upper()
    )
    print(f"[LAMBDA_PROC_PRECO] 'banco_cotacoes_atuais' atualizado para {ticker}.")

# --- Função Principal (Chamada pelo Worker) ---

def processar(ordem):
    """
    Função principal desta lambda.
    Recebe uma ordem, busca o preço, salva a transação e atualiza a cotação.
    """
    try:
        ticker = ordem['ticker']
        user_id = ordem['user_id']
        quantidade = ordem['quantidade']

        # 1. Buscar Preço (Serviço Lento Externo)
        preco_pago = _buscar_preco_ativo(ticker)
        
        if not preco_pago:
            print(f"[LAMBDA_PROC_PRECO] Falha ao processar {ticker}. Preço não encontrado.")
            return # Encerra o fluxo aqui

        # 2. Salvar no Banco de Transações
        db_transacoes = TinyDB(DB_TRANSACOES_PATH)
        transacao = {
            'user_id': user_id,
            'ticker': ticker.upper(),
            'quantidade': quantidade,
            'preco_pago': round(preco_pago, 2),
            'custo_total': round(preco_pago * quantidade, 2),
            'timestamp': str(datetime.now())
        }
        db_transacoes.insert(transacao)
        print(f"[LAMBDA_PROC_PRECO] Transação salva em 'banco_transacoes'.")

        # 3. Atualizar o Banco de Cotações
        _atualizar_cotacao_atual(ticker, preco_pago)

        # 4. Chamar a Próxima Lambda (Chaining)
        # Continua o fluxo passando o ID do usuário para a próxima etapa
        print(f"[LAMBDA_PROC_PRECO] Chamando 'lambda_consolidador' para o user_id: {user_id}...")
        lambda_consolidador.consolidar(user_id)

    except Exception as e:
        print(f"[LAMBDA_PROC_PRECO] ERRO CRÍTICO no processamento da ordem {ordem}: {e}")
        # (Em um sistema real, moveria a 'ordem' para uma fila de "falhas")
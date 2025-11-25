import os
from tinydb import TinyDB, Query

# --- Configuração de Path ---
# Pega o diretório raiz do projeto
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
DB_DIR = os.path.join(project_root, 'database')

# Garante que o diretório 'database' exista
os.makedirs(DB_DIR, exist_ok=True)

# Define os caminhos para nossos 3 "bancos" (arquivos JSON)
DB_TRANSACOES_PATH = os.path.join(DB_DIR, 'banco_transacoes.json')
DB_COTACOES_PATH = os.path.join(DB_DIR, 'banco_cotacoes_atuais.json')
DB_USUARIOS_PATH = os.path.join(DB_DIR, 'banco_usuarios.json')

def inicializar_bancos():
    """
    Cria (ou abre) os bancos de dados TinyDB e limpa qualquer dado antigo.
    Insere um usuário de teste para o fluxo funcionar.
    """
    print(f"Usando diretório de banco de dados: {DB_DIR}")

    # Conecta e limpa o banco de transações
    db_transacoes = TinyDB(DB_TRANSACOES_PATH)
    db_transacoes.truncate()  # Limpa a tabela (lista de documentos)
    print(f"Banco '{os.path.basename(DB_TRANSACOES_PATH)}' inicializado.")

    # Conecta e limpa o banco de cotações
    db_cotacoes = TinyDB(DB_COTACOES_PATH)
    db_cotacoes.truncate()
    print(f"Banco '{os.path.basename(DB_COTACOES_PATH)}' inicializado.")

    # Conecta, limpa e popula o banco de usuários
    db_usuarios = TinyDB(DB_USUARIOS_PATH)
    db_usuarios.truncate()
    
    # Insere um usuário de teste (ID 1) para que possamos comprar para ele
    db_usuarios.insert({
        'user_id': 1,
        'nome': 'Jair Teste',  # (Usando o nome que tínhamos como exemplo)
        'valor_total_carteira': 0.0
    })
    print(f"Banco '{os.path.basename(DB_USUARIOS_PATH)}' inicializado e usuário 'Jair Teste' (ID 1) inserido.")
    print("\nBancos de dados prontos!")

if __name__ == "__main__":
    inicializar_bancos()
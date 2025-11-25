import os

# Define o caminho raiz do projeto
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
DB_DIR = os.path.join(project_root, 'database')

# Define os caminhos para nossos 3 "bancos" (arquivos JSON)
# Alterado de .db para .json
DB_TRANSACOES_PATH = os.path.join(DB_DIR, 'banco_transacoes.json')
DB_COTACOES_PATH = os.path.join(DB_DIR, 'banco_cotacoes_atuais.json')
DB_USUARIOS_PATH = os.path.join(DB_DIR, 'banco_usuarios.json')
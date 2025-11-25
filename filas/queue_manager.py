# Este arquivo é o PONTO CENTRAL.
# Ele define as "constantes" para nosso servidor de filas (Manager)

# 1. A porta e "senha" para o servidor de filas
# (O servidor rodará dentro do app.py)
QUEUE_MANAGER_PORT = 50001
QUEUE_MANAGER_AUTHKEY = b'minha_senha_secreta_123'

# 2. Estes são os NOMES de registro para as filas.
# Pense neles como os "ramais" de telefone que usaremos
# para pedir cada fila ao gerente.
FILA_ORDENS = 'get_fila_ordens_validas'
FILA_PUSH = 'get_fila_notificacao_push'
FILA_EMAIL = 'get_fila_notificacao_email'
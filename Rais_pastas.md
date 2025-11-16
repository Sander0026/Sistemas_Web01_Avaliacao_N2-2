/projeto_carteira_aws/
|
|--- /api/
| |--- api.py # Nosso Gateway (Flask) que recebe as requisições
|
|--- /src/
| |--- /lambdas/ # Onde vive a lógica de negócio
| | |--- lambda_validador.py
| | |--- lambda_processador_preco.py
| | |--- lambda_consolidador.py
| | |--- lambda_notificador.py
| | |--- lambda_enviador_email.py
| |
| |--- /filas/
| |--- fila_ordens_validas.py
| |--- fila_notificacao_push.py
| |--- fila_notificacao_email.py
|
|--- /workers/
| |--- worker_ordens.py # Script que consome da Fila 1 (chama Lambda 2)
| |--- worker_push.py # Script que consome da Fila 2 (chama Lambda 4)
| |--- worker_email.py # Script que consome da Fila 3 (chama Lambda 5)
|
|--- /database/
| |--- init_db.py # Script para criar os 3 bancos e tabelas
| |--- banco_transacoes.db
| |--- banco_cotacoes_atuais.db
| |--- banco_usuarios.db
|
|--- requirements.txt # (flask, yfinance)
|--- README.md

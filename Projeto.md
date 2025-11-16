🚀 Resumo do Projeto: API de Carteira de Ações (Simulação AWS)

1. Conceito Principal

Vamos construir a arquitetura de backend para um simulador de compra de ações. O foco não é a interface (UI), mas sim simular um sistema de microsserviços moderno, assíncrono e robusto, muito similar ao que se faz na AWS (com API Gateway, Lambdas, SQS e DynamoDB).

Usaremos o Postman como nosso cliente (usuário) para enviar comandos.

2. A Arquitetura Híbrida

Nosso sistema terá dois fluxos de trabalho:

Fluxo Rápido (Síncrono): Para operações de leitura (ex: GET /transacoes). O Postman pergunta, a API busca no banco e responde na hora.

Fluxo Lento (Assíncrono): Para a operação principal (POST /comprar). Como essa operação é "lenta" (precisa buscar preço no Yahoo Finance, recalcular portfólio, etc.), a API não vai fazer o trabalho. Ela apenas aceita o pedido (responde 202 Accepted), joga em uma fila e encerra a chamada. Outros processos (Workers) farão o trabalho pesado em segundo plano.

3. Inventário de Componentes

Aqui está o nome de cada "peça" do nosso sistema:

⚙️ "Lambidas" (Nossa Lógica de Negócio) - 5 Funções
Estas são as funções Python que fazem o trabalho, cada uma em seu próprio arquivo em src/lambdas/:

lambda_validador.py

O que faz: Valida o JSON da ordem de compra (se tem ticker, user_id, qtd). É chamada pela API.

lambda_processador_preco.py

O que faz: É o "trabalho sujo".

Conecta na API Externa (Yahoo Finance) para buscar o preço.

Salva a transação no banco_transacoes.

Atualiza o preço do ativo no banco_cotacoes_atuais.

Chama a próxima lambda (lambda_consolidador).

lambda_consolidador.py

O que faz: Recalcula o valor total da carteira do usuário.

Lê os bancos transacoes e cotacoes.

Atualiza o valor total no banco_usuarios.

Dispara as duas notificações, colocando-as nas filas de PUSH e EMAIL.

lambda_notificador.py

O que faz: Simula o envio de uma notificação PUSH. (No nosso caso, vai dar um print no console do Worker 2).

lambda_enviador_email.py

O que faz: Simula o envio de um E-MAIL. (No nosso caso, vai dar um print no console do Worker 3).

🗳️ Filas (Nossa "Esteira" SQS) - 3 Filas
Estas são as "esteiras" que conectam os serviços. Serão gerenciadas por um queue_manager.py (usando multiprocessing.Manager e multiprocessing.Queue).

fila_ordens_validas

Fluxo: API => Worker 1

Propósito: Guarda as ordens de compra que já foram validadas e estão prontas para serem processadas (ter o preço buscado).

fila_notificacao_push

Fluxo: Lambda 3 => Worker 2

Propósito: Guarda as mensagens de notificação PUSH.

fila_notificacao_email

Fluxo: Lambda 3 => Worker 3

Propósito: Guarda as mensagens de notificação de E-MAIL.

🗃️ Bancos de Dados (Nosso "Armazém") - 3 Bancos
Usaremos 3 bancos de dados SQLite separados para simular microsserviços (cada um dono de seus dados).

banco_transacoes.db

Propósito: Guarda o histórico de todas as compras (ex: "User 1 comprou 10 PETR4 por R$ 40,50").

banco_cotacoes_atuais.db

Propósito: Guarda o último preço conhecido de cada ativo (ex: "PETR4 = R$ 40,50").

banco_usuarios.db

Propósito: Guarda o perfil do usuário e o valor total atualizado de sua carteira (ex: "User 1 tem R$ 10.500,00").

4. Como o Sistema Roda (Execução)
   Para o projeto funcionar, precisaremos rodar 4 processos em 4 terminais separados:

Terminal 1 (O Gateway): python api/api.py

Roda a API Flask e inicia o servidor de Filas (queue_manager).

Terminal 2 (Worker de Ordens): python workers/worker_ordens.py

Conecta-se à fila_ordens_validas (Fila 1).

Quando uma ordem chega, ele executa a lambda_processador_preco e a lambda_consolidador.

Terminal 3 (Worker de PUSH): python workers/worker_push.py

Conecta-se à fila_notificacao_push (Fila 2).

Executa a lambda_notificador.

Terminal 4 (Worker de EMAIL): python workers/worker_email.py

Conecta-se à fila_notificacao_email (Fila 3).

Executa a lambda_enviador_email.

5. O Teste (Como mostrar para o professor)
   Nosso teste é 100% via Postman e os logs dos terminais:

TESTE 1 (Consultar): Damos um GET /usuarios/1. O Postman vai mostrar: {"valor_total_carteira": 0.00}.

TESTE 2 (Comprar): Damos um POST /comprar (enviando 10 PETR4). O Postman vai receber 202 Accepted imediatamente.

(Magia): O professor verá os terminais 2, 3 e 4 mostrarem os logs de "processando...", "consolidando...", "notificação push...", "email enviado...".

TESTE 3 (Confirmar): Após 5 segundos, damos o GET /usuarios/1 de novo. O Postman agora vai mostrar: {"valor_total_carteira": 405.50} (ou o valor que for).

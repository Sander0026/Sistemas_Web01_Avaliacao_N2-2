# 🚀 API de Carteira de Ações (Simulação de Arquitetura Serverless)

Este projeto é uma avaliação para a disciplina de Sistemas Web, com o objetivo de demonstrar a implementação de uma arquitetura web moderna, complexa e assíncrona.

## 💡 A Ideia e a Complexidade

O projeto simula uma **API de backend para um portfólio de ações**.

A **criatividade e complexidade** do projeto não estão na funcionalidade (o "quê" - comprar ações), mas sim na **arquitetura (o "como")**. O sistema foi desenhado para simular uma arquitetura de microsserviços _serverless_ (como a da AWS), com os seguintes componentes:

- **API Gateway (Flask):** O `app.py` atua como o portão de entrada único, recebendo requisições HTTP do cliente (Postman).
- **Filas (SQS):** O `multiprocessing.Manager` é usado para simular um serviço de filas de mensagens em rede (como o AWS SQS). Isso **desacopla** a API dos serviços de processamento.
- **Lambdas (Funções):** A pasta `src/lambdas` contém toda a lógica de negócio, simulando funções serverless (como o AWS Lambda).
- **Workers (Consumidores):** Os 3 scripts na pasta `workers/` atuam como consumidores independentes das filas, processando as mensagens em paralelo.
- **Bancos de Dados NoSQL (DynamoDB):** O `TinyDB` é usado para simular bancos de dados de documentos (`.json`), onde cada microsserviço (transações, usuários, cotações) gerencia seus próprios dados.

### Padrões de Arquitetura Implementados:

1.  **Processamento Assíncrono:** A API responde ao usuário **imediatamente** (`HTTP 202 Accepted`) após validar e enfileirar a ordem, sem esperar o processamento lento (busca de preço, recálculo de portfólio).
2.  **Fan-Out (Leque):** Uma única ação (compra) dispara múltiplos eventos paralelos. O `lambda_consolidador` coloca mensagens em **duas filas** diferentes (`PUSH` e `EMAIL`), que são consumidas por workers diferentes.
3.  **Chaining (Encadeamento):** O `lambda_processador_preco` chama o `lambda_consolidador` diretamente, criando uma cadeia de processamento.

---

## 🗺️ Diagrama de Arquitetura

O fluxo visual completo dos microsserviços, filas e bancos de dados está disponível no arquivo:
`/docs/Sistemas_Web01_Avaliacao_N2-2.drawio.png`

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **Flask:** Para a API Gateway.
- **multiprocessing.Manager:** Para simular o barramento de filas entre processos.
- **TinyDB:** Para simular os bancos de dados NoSQL (arquivos `.json`).
- **yfinance:** Para consumir a API externa do Yahoo Finance e obter preços reais das ações.

---

## ⚙️ Como Executar o Projeto

Para rodar o sistema, você precisará de **4 terminais** abertos simultaneamente.

### 1. Pré-requisitos

- Ter o Python 3.10 ou superior instalado.
- Ter o Postman (ou similar) para testar a API.

### 2. Instalação

1.  Clone o repositório (ou tenha a pasta do projeto).
2.  Crie e ative um ambiente virtual:

    ```bash
    python -m venv .venv

    # No Windows PowerShell (pode precisar rodar Set-ExecutionPolicy)
    Set-ExecutionPolicy RemoteSigned -Scope Process
    .\.venv\Scripts\Activate.ps1
    ```

3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Importante:** Inicialize os bancos de dados (arquivos `.json`) pela primeira vez:
    ```bash
    python database/init_db.py
    ```

### 3. Execução (Os 4 Terminais)

Abra 4 terminais separados, ative o ambiente virtual (`.\.venv\Scripts\Activate.ps1`) em cada um, e rode os seguintes comandos:

**➡️ Terminal 1: O Servidor (API + Gerenciador de Filas)**
(Este é o "cérebro" do sistema)

```bash
Set-ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
python app.py 
```

**➡️ Terminal 2: O worker**


```bash
Set-ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
python .\workers\worker_email.py 
```

**➡️ Terminal 3: O workers**

```bash
Set-ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
python .\workers\worker_ordens.py 
```

**➡️ Terminal 4: O worker**

```bash
Set-ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1

```

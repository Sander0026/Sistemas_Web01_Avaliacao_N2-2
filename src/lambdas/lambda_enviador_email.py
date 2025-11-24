import sys
import os
from datetime import datetime

# --- Configuração de Path ---
# Adiciona o diretório raiz do projeto ao path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.append(project_root)

def enviar(mensagem):
    """
    Função principal desta lambda.
    Recebe uma mensagem da fila EMAIL e a exibe no console, simulando
    o envio para um serviço de E-mail Transacional (como o AWS SES ou SendGrid).
    """
    try:
        user_id = mensagem.get('user_id', 'N/A')
        assunto = mensagem.get('assunto', 'Sem Assunto')
        valor = mensagem.get('valor', 'N/A')
        timestamp = str(datetime.now())

        # Esta é a "simulação" do envio
        # Este print aparecerá no terminal onde o 'worker_email.py' está a rodar
        print(f"[LAMBDA_ENVIADOR_EMAIL] [EMAIL ENVIADO 📧]")
        print(f"  > Timestamp: {timestamp}")
        print(f"  > Para UserID: {user_id}")
        print(f"  > Assunto: \"{assunto}\"")
        print(f"  > Valor Carteira: {valor}")
        
        # Em um projeto real, aqui haveria uma chamada a uma API de email
        # ex: requests.post("https://api.sendgrid.com/v3/mail/send", json=...)
        
    except Exception as e:
        print(f"[LAMBDA_ENVIADOR_EMAIL] ❌ ERRO ao simular envio de email para {mensagem}: {e}")
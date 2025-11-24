import sys
import os
from datetime import datetime

# Adiciona o diretório raiz do projeto ao path para imports futuros (embora não seja 
# estritamente necessário para este script simples, é uma boa prática mantê-lo)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.append(project_root)

def notificar(mensagem):
    """
    Função principal desta lambda.
    Recebe uma mensagem da fila PUSH e a exibe no console, simulando
    o envio para um serviço de Notificação Push (como o Firebase ou AWS SNS).
    """
    try:
        user_id = mensagem.get('user_id', 'N/A')
        texto_msg = mensagem.get('mensagem', 'Mensagem vazia')
        timestamp = str(datetime.now())

        # Esta é a "simulação" do envio
        # Este print aparecerá no terminal onde o 'worker_push.py' está a rodar
        print(f"[LAMBDA_NOTIFICADOR] [PUSH ENVIADO 📱]")
        print(f"  > Timestamp: {timestamp}")
        print(f"  > Para UserID: {user_id}")
        print(f"  > Mensagem: \"{texto_msg}\"")
        
        # Em um projeto real, aqui haveria uma chamada HTTP para o Firebase/SNS
        # ex: requests.post("https://api.push.service/send", json=mensagem)
        
    except Exception as e:
        print(f"[LAMBDA_NOTIFICADOR] ❌ ERRO ao simular notificação push para {mensagem}: {e}")
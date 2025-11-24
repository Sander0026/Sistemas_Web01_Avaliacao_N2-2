def validar_ordem(ordem):
    """
    Valida se a ordem de compra contém os campos necessários.
    """
    if not isinstance(ordem, dict):
        return False
    
    required_fields = ['user_id', 'ticker', 'quantidade'] # Campos obrigatórios
    for field in required_fields:
        if field not in ordem:
            return False
            
    # Verifica tipos básicos, pode ser expandido conforme necessário
    if not isinstance(ordem['user_id'], int) or not isinstance(ordem['ticker'], str) or not isinstance(ordem['quantidade'], int):
        return False

    return True

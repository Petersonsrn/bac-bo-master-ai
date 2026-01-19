import random

def analisar_padrao(historico):
    """
    Analisa a lista de resultados e tenta encontrar padrões.
    P = Player (Azul) | B = Banker (Vermelho) | E = Empate
    """
    # Se tiver poucos dados, não faz nada
    if len(historico) < 3:
        return "Dados insuficientes, aguardando..."

    ultimos_3 = historico[-3:] # Pega os 3 últimos
    
    # --- ESTRATÉGIA 1: SURF (Seguir a tendência) ---
    # Se saiu 3 iguais, a chance de continuar é considerada alta por apostadores (embora matematicamente seja 50%)
    if ultimos_3 == ['B', 'B', 'B']:
        return "Sinal: SURF NO BANKER (🔴 Aposte Vermelho)"
    elif ultimos_3 == ['P', 'P', 'P']:
        return "Sinal: SURF NO PLAYER (🔵 Aposte Azul)"

    # --- ESTRATÉGIA 2: QUEBRA (Xadrez) ---
    # Se está alternando P B P, a tendência é continuar alternando
    if ultimos_3 == ['P', 'B', 'P']:
        return "Sinal: XADREZ (🔴 Aposte Vermelho para manter a troca)"
    elif ultimos_3 == ['B', 'P', 'B']:
        return "Sinal: XADREZ (🔵 Aposte Azul para manter a troca)"

    # --- ESTRATÉGIA 3: REPETIÇÃO DUPLA ---
    # P P B B ... ?
    if len(historico) >= 4:
        ultimos_4 = historico[-4:]
        if ultimos_4 == ['P', 'P', 'B', 'B']:
            return "Sinal: DUPLA (🔵 Aposte Azul para formar par)"
        if ultimos_4 == ['B', 'B', 'P', 'P']:
            return "Sinal: DUPLA (🔴 Aposte Vermelho para formar par)"

    return "Aguardando padrão claro..."

# --- SIMULAÇÃO DO BOT ---
if __name__ == "__main__":
    print("=== BOT DE SINAIS BACCARAT 1.0 ===")
    print("Digite os resultados: p (azul), b (vermelho) ou e (empate)")
    print("Digite 'fim' para sair.")
    
    historico_atual = []
    
    while True:
        try:
            entrada = input(f"\nHistórico Atual: {historico_atual}\nNovo resultado? ").strip().lower()
        except EOFError:
            break
            
        if entrada == 'fim':
            break
        
        if entrada in ['p', 'b', 'e']:
            historico_atual.append(entrada.upper())
            sinal = analisar_padrao(historico_atual)
            print(f"⚡ {sinal}")
        else:
            print("Entrada inválida! Digite apenas p, b ou e.")

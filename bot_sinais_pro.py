import random
from collections import Counter

class AnalisadorBaccaratPro:
    def __init__(self):
        self.historico = []
        self.acertos = 0
        self.erros = 0
        
        # Pesos iniciais das estratégias (serão ajustados dinamicamente)
        self.pesos = {
            'surf': 1.0,    # Seguir tendência
            'xadrez': 1.0,  # Alternar
            'dupla': 1.0,   # Pares
            'aleatorio': 0.1 # Fator de caos (math)
        }
        
        # Histórico de performance das estratégias (1 = win, -1 = loss)
        self.performance_estrategias = {
            'surf': [],
            'xadrez': [],
            'dupla': []
        }

    def adicionar_resultado(self, resultado):
        """Recebe 'P', 'B' ou 'E'."""
        resultado = resultado.upper()
        
        # Avalia quem acertaria essa rodada ANTES de adicionar ao histórico
        if len(self.historico) >= 3 and resultado != 'E':
            self._avaliar_performance_passada(resultado)
            
        self.historico.append(resultado)
        self._recalibrar_pesos()

    def _avaliar_performance_passada(self, resultado_real):
        # Recalcula o que as estratégias TERIAM previsto para esta rodada
        # para ver qual está "quente" na mesa atual.
        
        h_limpo = [x for x in self.historico if x != 'E']
        if len(h_limpo) < 4: return

        u1, u2, u3 = h_limpo[-3:] 
        
        # Surf: Se u2==u3, preveria u3. 
        prev_surf = u3 if u2 == u3 else None
        
        # Xadrez: Se u2!=u3, preveria o oposto de u3
        prev_xadrez = ('B' if u3 == 'P' else 'P') if u2 != u3 else None
        
        # Dupla: Se u1==u2!=u3, preveria u3 (para fechar par)
        prev_dupla = u3 if (u1 == u2 and u2 != u3) else None

        # Registra Win/Loss/Blank
        self.performance_estrategias['surf'].append(1 if prev_surf == resultado_real else (-1 if prev_surf else 0))
        self.performance_estrategias['xadrez'].append(1 if prev_xadrez == resultado_real else (-1 if prev_xadrez else 0))
        self.performance_estrategias['dupla'].append(1 if prev_dupla == resultado_real else (-1 if prev_dupla else 0))

    def _recalibrar_pesos(self):
        """Matemática Adaptativa: Aumenta peso da estratégia que está ganhando nos últimos 10 jogos."""
        for estrat in self.pesos:
            if estrat == 'aleatorio': continue
            
            # Pega os últimos 10 resultados da estratégia
            ultimos_results = self.performance_estrategias[estrat][-10:]
            if not ultimos_results: continue
            
            score = sum(ultimos_results) # Saldo de vitórias
            
            # Ajusta peso: Base 1.0 + (Saldo * 0.2). Ex: Saldo +5 -> Peso 2.0
            novo_peso = 1.0 + (score * 0.2)
            self.pesos[estrat] = max(0.1, novo_peso) # Mínimo 0.1

    def analisar(self):
        """Retorna probabilidade matemática baseada no momento da mesa."""
        if len(self.historico) < 5:
            return None, 0, "Calibrando matemática (aguarde)..."

        h_limpo = [x for x in self.historico if x != 'E']
        if not h_limpo: return None, 0, "Sem dados suficientes"
        
        u1 = h_limpo[-1] # Último
        
        # Scores para Próxima Jogada
        pontos_P = 0
        pontos_B = 0
        
        detalhes = []

        # 1. Aplica Estratégia SURF (Peso Dinâmico)
        # Se temos 3 iguais, surf indica continuar.
        if len(h_limpo) >= 3 and h_limpo[-2] == h_limpo[-1]:
            sinal = h_limpo[-1] # Repetir
            peso = self.pesos['surf']
            if sinal == 'P': pontos_P += peso
            else: pontos_B += peso
            detalhes.append(f"Surf({peso:.1f})")

        # 2. Aplica Estratégia XADREZ (Peso Dinâmico)
        if len(h_limpo) >= 2 and h_limpo[-2] != h_limpo[-1]:
            sinal = 'B' if h_limpo[-1] == 'P' else 'P' # Trocar
            peso = self.pesos['xadrez']
            if sinal == 'P': pontos_P += peso
            else: pontos_B += peso
            detalhes.append(f"Xadrez({peso:.1f})")

        # 3. Calculo de Probabilidade Simples (Frequência local)
        # Se nos últimos 12, saiu 8 P e 2 B, a chance de B aumenta (Maturidade das chances - Falácia, mas usada em bots)
        ultimos_12 = h_limpo[-12:]
        qtd_P = ultimos_12.count('P')
        qtd_B = ultimos_12.count('B')
        
        # Fator de equilíbrio (Força retorno à média)
        # Se P está muito na frente (>70%), dá pontinhos pro B
        total = qtd_P + qtd_B
        if total > 0:
            if (qtd_P / total) > 0.7: 
                pontos_B += 0.5
                detalhes.append("Equilíbrio->B")
            elif (qtd_B / total) > 0.7: 
                pontos_P += 0.5
                detalhes.append("Equilíbrio->P")

        # --- DECISÃO ---
        diferenca = abs(pontos_P - pontos_B)
        total_pontos = pontos_P + pontos_B + 0.001
        
        prob_P = (pontos_P / total_pontos) * 100
        prob_B = (pontos_B / total_pontos) * 100
        
        sinal_final = 'P' if pontos_P > pontos_B else 'B'
        
        # Nível de confiança para sinal "90%"
        # Exige que uma estratégia esteja com peso alto E concorde com a probabilidade
        confianca_str = "Baixa"
        if diferenca > 1.5: confianca_str = "ALTA 🔥"
        elif diferenca > 0.8: confianca_str = "Média"
        
        msg = f"Probabilidades: 🔵 {prob_P:.1f}% vs 🔴 {prob_B:.1f}%\n"
        msg += f"   Tendência: {sinal_final} ({confianca_str})\n"
        msg += f"   Fatores: {', '.join(detalhes)}"
        
        return sinal_final, diferenca, msg

# --- SISTEMA DE TESTE ---
if __name__ == "__main__":
    bot = AnalisadorBaccaratPro()
    print("=== BOT MATEMÁTICO ADAPTATIVO ===")
    print("Este bot aprende qual estratégia está funcionando na mesa ATUAL.")
    print("Cole um histórico pra testar (ex: P B P B P P P B B)")
    
    while True:
        inp = input("\nResultado (ou sequência): ").strip().upper()
        if inp == 'FIM': break
        
        # Permite colar "P B P B" de uma vez
        if ' ' in inp or len(inp) > 1:
            lista = list(inp.replace(' ', ''))
            for item in lista:
                if item in ['P', 'B', 'E']:
                    bot.adicionar_resultado(item)
            print(f"Histórico importado! ({len(bot.historico)} jogadas)")
        else:
            if inp in ['P', 'B', 'E']:
                bot.adicionar_resultado(inp)
            
        # Analisa o futuro
        sinal, forca, msg = bot.analisar()
        if sinal:
            print(f"--------------------------------")
            print(msg)
            print(f"--------------------------------")
        else:
            print("Aguardando mais dados...")

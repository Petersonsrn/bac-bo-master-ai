
from baccarat_engine import BaccaratEngine
import csv
import datetime

class BaccaratEnginePro(BaccaratEngine):
    """
    Motor Avançado com Derived Roads (Estradas Derivadas) Reais.
    Implementa: Big Eye Boy, Small Road, Cockroach Pig.
    E AGORA: Peso Adaptativo (Foca em quem está acertando).
    """

    def __init__(self):
        super().__init__()
        # Pesos iniciais: Surf (Tendência) e Xadrez (Reversão)
        self.stats_weights = {
            'surf': 1.0, 
            'xadrez': 1.0, 
            'roads': 1.2
        }
        # Resultados virtuais para saber quem estaria ganhando
        self.virtual_scores = {
            'surf': [],
            'xadrez': [],
            'roads': []
        }

    def add_result(self, res):
        # 1. Avalia quem acertou NA RODADA PASSADA (Virtual Check)
        if len(self.raw_history) >= 2 and res != 'E':
            last_res = self.raw_history[-1]
            actual = res
            
            # Surf: Teria apostado no mesmo
            win_surf = 1 if last_res == actual else -1
            self.virtual_scores['surf'].append(win_surf)
            
            # Xadrez: Teria apostado no oposto
            opp = 'B' if last_res == 'P' else 'P'
            win_xad = 1 if opp == actual else -1
            self.virtual_scores['xadrez'].append(win_xad)
            
            # Ajusta Pesos (Média Móvel de 8 jogadas)
            for k in ['surf', 'xadrez']:
                scores = self.virtual_scores[k][-8:]
                total = sum(scores)
                # Se total > 0, estratégia está ganhando -> Aumenta peso
                # Se total < 0, estratégia está perdendo -> Diminui peso
                self.stats_weights[k] = max(0.2, 1.0 + (total * 0.25))

        super().add_result(res)

    def get_road_signal(self):
        """
        Analisa as 3 estradas derivadas e retorna o consenso.
        """
        if len(self.raw_history) < 5: return None, "Formando estradas..."
        
        match_p = self._check_derived_roads('P')
        match_b = self._check_derived_roads('B')
        
        score_p = match_p['big_eye'] + match_p['small'] + match_p['cockroach']
        score_b = match_b['big_eye'] + match_b['small'] + match_b['cockroach']
        
        if score_p > score_b and score_p >= 2:
            return 'P', f"Padrão Derivado Confirmado (Força {score_p}/3)"
        elif score_b > score_p and score_b >= 2:
            return 'B', f"Padrão Derivado Confirmado (Força {score_b}/3)"
            
        return None, "Estradas conflitantes (Neutro)"

    def _check_derived_roads(self, simulation_next):
       # ... (Lógica das estradas mantida igual)
        temp_hist = self.raw_history + [simulation_next]
        results = {'big_eye': 0, 'small': 0, 'cockroach': 0}
        
        if len(temp_hist) > 5:
            # Big Eye
            if temp_hist[-1] == temp_hist[-2]: results['big_eye'] = 1 
            if temp_hist[-1] != temp_hist[-2] and temp_hist[-2] != temp_hist[-3]: results['big_eye'] = 1
            # Small Road
            if len(temp_hist) > 6 and temp_hist[-1] == temp_hist[-3]: results['small'] = 1
            # Cockroach
            if len(temp_hist) > 8 and temp_hist[-1] == temp_hist[-4]: results['cockroach'] = 1
            
        return results

    def predict_advanced(self):
        """
        Hybrid Intelligence 4.0: PESA O QUE ESTÁ FUNCIONANDO.
        """
        if not self.raw_history: return None, "Aguardando..."
        
        h = [x for x in self.raw_history if x != 'E']
        if len(h) < 2: return None, "Dados insuficientes"

        # --- 1. OVERRIDES (Dragon / Sniper) ---
        # Dragon 5+
        if len(h) >= 5 and len(set(h[-5:])) == 1:
             return h[-1], 98, "🐉 SUPER DRAGON (Surf Obrigatório)"
        
        # Sniper (Padrões Perfeitos)
        sniper, sn_reason = self.check_sniper_patterns(h)
        if sniper:
             # Só obedece sniper se o peso do Surf não for Absurdo (Dragão Oculto)
             if self.stats_weights['surf'] > 2.5 and sniper != h[-1]:
                 return h[-1], 90, f"Surf muito forte ({self.stats_weights['surf']:.1f}) atropelando Sniper"
             return sniper, 95, f"🔫 {sn_reason}"

        # --- 2. VOTAÇÃO PONDERADA (Adaptação ao Momento) ---
        votes_P = 0.0
        votes_B = 0.0
        
        last = h[-1]
        
        # Voto SURF (Seguir a tendência)
        w_surf = self.stats_weights['surf']
        if last == 'P': votes_P += w_surf
        else: votes_B += w_surf
        
        # Voto XADREZ (Quebrar tendência)
        w_xad = self.stats_weights['xadrez']
        opp = 'B' if last == 'P' else 'P'
        if opp == 'P': votes_P += w_xad
        else: votes_B += w_xad
        
        # Voto ROADS
        r_sig, r_reason = self.get_road_signal()
        w_roads = self.stats_weights['roads']
        if r_sig == 'P': votes_P += w_roads
        elif r_sig == 'B': votes_B += w_roads
        
        # --- 3. DECISÃO FINAL ---
        total_votes = votes_P + votes_B
        if total_votes == 0: return None, 0, "Sem dados"

        winner = 'P' if votes_P > votes_B else 'B'
        winning_votes = votes_P if winner == 'P' else votes_B
        
        # Probabilidade Matemática
        prob = int((winning_votes / total_votes) * 100)
        
        # Bonus de Confiança se estratégias concordarem
        if w_surf > 1.5 and w_roads > 1.5: prob += 5
        prob = min(99, prob) # Teto 99%
        
        # Nome da estratégia vencedora para mostrar ao user
        winning_strat = "Surf (Tendência)" if w_surf > w_xad else "Xadrez (Reversão)"
        if w_roads > max(w_surf, w_xad) + 0.5: winning_strat = "Roads (Derivadas)"
        
        reason = f"Modo: {winning_strat} (P:{votes_P:.1f} vs B:{votes_B:.1f})"
            
        return winner, prob, reason

    def check_sniper_patterns(self, h):
        # h já vem sem empates
        if len(h) < 3: return None, None
        
        # Surf (3+ iguais) 
        if h[-1] == h[-2] == h[-3]:
             return h[-1], f"Surf de {h[-1]} (3x)"
             
        # Ping Pong (3+ alternados: P B P) -> Aposta B
        if h[-1] != h[-2] and h[-2] != h[-3]:
             opp = 'B' if h[-1] == 'P' else 'P'
             return opp, "Xadrez / Ping-Pong (Padrão 1-1)"
             
        # Padrão 2-1 (P P B) -> Aposta B (Quebra de Segunda) vs P (Volta pra 2)?
        # Estratégia comum: Apostar na repetição da segunda perna para formar par
        if len(h) >= 3:
             if h[-2] == h[-3] and h[-1] != h[-2]:
                 # Ex: P P B ... aposta B para fazer P P B B
                 return h[-1], "Formação de Par (2-2)"
        
        # Padrão 2-2 (P P B B) -> Aposta P (Quebra de dupla)
        if len(h) >= 4:
            if h[-1] == h[-2] and h[-3] == h[-4] and h[-2] != h[-3]:
                # Temos par atual e par anterior
                # Ex: P P B B ... aposta P
                opp = 'B' if h[-1] == 'P' else 'P'
                return opp, "Quebra de Dupla (Sequência 2-2)"

        return None, None
    
    def export_csv(self):
        try:
            with open('sessao_baccarat.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Index", "Result", "Timestamp"])
                for i, res in enumerate(self.raw_history):
                    writer.writerow([i+1, res, datetime.datetime.now().strftime("%H:%M:%S")])
        except:
            pass

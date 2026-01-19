
import random

class BaccaratEngine:
    """
    Engine Adaptativa de Nível Profissional "Chameleon".
    Testa múltiplas estratégias em tempo real e usa a que está ganhando na mesa.
    """
    def __init__(self):
        self.raw_history = [] 
        self.last_mc_probs = (50, 50)
        
        # Definição das Estratégias Virtuais
        self.strategies = {
            'FOLLOW': self._strat_follow,    # Segue o último (Surf)
            'FLIP': self._strat_flip,        # Oposto do último (Xadrez)
            'REPEAT_2': self._strat_repeat2, # Repete o penúltimo
            'FLIP_2': self._strat_flip2,     # Oposto do penúltimo
            'MAJORITY': self._strat_majority # Maioria dos últimos 5
        }

    def add_result(self, result):
        res = result.upper()
        if res in ['P', 'B', 'E']:
            self.raw_history.append(res)

    def get_stats(self):
        total = len(self.raw_history)
        if total == 0: return {'P': 0, 'B': 0, 'E': 0, 'total': 0}
        p = self.raw_history.count('P')
        b = self.raw_history.count('B')
        e = self.raw_history.count('E')
        return {'P': round((p/total)*100, 1), 'B': round((b/total)*100, 1), 'E': round((e/total)*100, 1), 'total': total}

    # --- SIMULADOR DE ESTRATÉGIAS ---
    
    def _strat_follow(self, history):
        # Aposta no último resultado
        if not history: return None
        return history[-1]

    def _strat_flip(self, history):
        # Aposta contra o último
        if not history: return None
        last = history[-1]
        return 'B' if last == 'P' else 'P'

    def _strat_repeat2(self, history):
        # Olha 2 atrás. Ex: P B ... (aposta P)
        if len(history) < 2: return None
        return history[-2]

    def _strat_flip2(self, history):
        if len(history) < 2: return None
        val = history[-2]
        return 'B' if val == 'P' else 'P'

    def _strat_majority(self, history):
        # Maioria dos ultimos 5
        if len(history) < 5: return None
        recent = history[-5:]
        if recent.count('P') > recent.count('B'): return 'P'
        return 'B'

    def find_best_strategy(self):
        """
        Roda um Backtest nas últimas 15 rodadas para ver qual estratégia
        está com maior taxa de acerto (Win Rate).
        """
        history = [x for x in self.raw_history if x != 'E']
        if len(history) < 5: return None, 0
        
        # Testar nos últimos N resultados
        test_range = min(len(history)-1, 15)
        scores = {name: 0 for name in self.strategies}
        
        # Loop "virtual" do passado
        for i in range(len(history) - test_range, len(history)):
            # O que a mesa era ANTES deste resultado?
            past_slice = history[:i]
            actual_result = history[i]
            
            for name, func in self.strategies.items():
                prediction = func(past_slice)
                if prediction == actual_result:
                    scores[name] += 1
                # Penalidade para erro consecutivo (opcional)
        
        # Melhor estratégia
        best_name = max(scores, key=scores.get)
        best_score = scores[best_name]
        win_rate = (best_score / test_range) * 100
        
        return best_name, win_rate

    def predict_advanced(self):
        """
        Nova Lógica: Seleção Natural de Estratégias.
        """
        clean_hist = [x for x in self.raw_history if x != 'E']
        if len(clean_hist) < 3:
            return None, "Analisando DNA da mesa..."

        # 1. Descobrir a estratégia dominante agora
        best_strat_name, win_rate = self.find_best_strategy()
        
        if win_rate < 50:
            return None, "Mercado sem padrão (WR < 50%). Aguarde."
            
        # 2. Usar a melhor estratégia para prever o FUTURO
        func = self.strategies[best_strat_name]
        prediction = func(clean_hist)
        
        if not prediction: return None, "Dados insuficientes."
        
        # 3. Metadados para display
        strategy_display = {
            'FOLLOW': "Tendência de Surf 🏄",
            'FLIP': "Padrão Ping-Pong ♟️",
            'REPEAT_2': "Ciclo de 2ª Ordem",
            'FLIP_2': "Quebra de 2ª Ordem",
            'MAJORITY': "Força da Maioria"
        }
        
        desc = strategy_display.get(best_strat_name, best_strat_name)
        confidence = "Média"
        if win_rate > 75: confidence = "ALTA 💎"
        elif win_rate > 60: confidence = "Boa"
        
        # Simular Probabilidade Visual baseada no WinRate
        # Se WR é 80%, mostramos barra perto de 80%
        final_prob = int(win_rate) + random.randint(-2, 2)
        if prediction == 'P':
            self.last_mc_probs = (final_prob, 100-final_prob)
            return 'P', f"{desc} (Assertividade: {int(win_rate)}%)\n   Melhor Estratégia dos ultimos 15 jogos."
        else:
            self.last_mc_probs = (100-final_prob, final_prob)
            return 'B', f"{desc} (Assertividade: {int(win_rate)}%)\n   Melhor Estratégia dos ultimos 15 jogos."

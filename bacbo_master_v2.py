import customtkinter as ctk
import pyautogui
import threading
import time
import mss
import colorsys
import json
import os
import math

# --- CONFIGURAÇÃO GLOBAL ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Cores Visuais (UI)
C_PLAYER = "#4169E1" # Royal Blue
C_BANKER = "#DC143C" # Crimson
C_TIE    = "#00FA9A" # Medium Spring Green
C_BG     = "#0F0F0F" # Almost Black
C_PANEL  = "#1C1C1C" # Dark Gray

# --- CÉREBRO DO BOT (MOTOR DE PREVISÃO REFEITO) ---
class BaccaratBrain:
    def __init__(self):
        self.history = []
        self.strategies = {
            'trend': {'score': 0, 'weight': 1.0, 'name': 'Surf de Tendência'},
            'chop':  {'score': 0, 'weight': 1.0, 'name': 'Xadrez / Reversão'},
            'pattern': {'score': 0, 'weight': 1.2, 'name': 'Detector de Padrões'}
        }

    def reset(self):
        self.history = []
        self.reset_weights()

    def reset_weights(self):
        for k in self.strategies:
            self.strategies[k]['weight'] = 1.0

    def add_result(self, res):
        if not res or res == 'E': return
        self.history.append(res)
        self._learn_from_mistakes()

    def _learn_from_mistakes(self):
        # Auto-ajuste de pesos baseado no último resultado
        if len(self.history) < 2: return
        
        last_real = self.history[-1]
        prev_real = self.history[-2]
        
        # Quem teria acertado?
        
        # Trend (Surf): Apostaria que o atual seria igual ao anterior
        hit_trend = (last_real == prev_real)
        
        # Chop (Xadrez): Apostaria que o atual seria diferente do anterior
        hit_chop = (last_real != prev_real)
        
        # Ajusta Pesos
        if hit_trend: self.strategies['trend']['weight'] += 0.1
        else: self.strategies['trend']['weight'] = max(0.5, self.strategies['trend']['weight'] - 0.05)
        
        if hit_chop: self.strategies['chop']['weight'] += 0.1
        else: self.strategies['chop']['weight'] = max(0.5, self.strategies['chop']['weight'] - 0.05)

    def predict(self):
        """Retorna: (Sinal, Probabilidade%, Motivo)"""
        if len(self.history) < 3:
            return None, 0, "Aguardando mais dados..."

        votes = {'P': 0.0, 'B': 0.0}
        reasons = []

        # 1. ANÁLISE DE PADRÕES (Weight 1.2+)
        # Sequência P (Surf)
        streak = 0
        current_streak_char = self.history[-1]
        for x in reversed(self.history):
            if x == current_streak_char: streak += 1
            else: break
            
        w_pattern = self.strategies['pattern']['weight']
        
        # Super Dragon (5+)
        if streak >= 5:
            votes[current_streak_char] += 5.0 # Peso massivo
            reasons.append(f"🐉 DRAGON ({streak}x)")
        # Snipers
        elif len(self.history) >= 4:
            # 2-2 (P P B B)
            if self.history[-1] == self.history[-2] and self.history[-3] == self.history[-4] and self.history[-2] != self.history[-3]:
                 # Quebra da dupla? Ou segue? O padrão 2-2 sugere mudar
                 opp = 'B' if current_streak_char == 'P' else 'P'
                 votes[opp] += w_pattern * 2
                 reasons.append("Padrão 2-2 Completo")

        # 2. ANÁLISE TENDÊNCIA vs REVERSÃO
        w_trend = self.strategies['trend']['weight']
        w_chop = self.strategies['chop']['weight']
        
        # Trend aposta no último
        votes[self.history[-1]] += w_trend
        
        # Chop aposta no oposto
        s_opp = 'B' if self.history[-1] == 'P' else 'P'
        votes[s_opp] += w_chop
        
        # --- CONSENSO ---
        total_score = votes['P'] + votes['B']
        if total_score == 0: return None, 0, "Neutro"
        
        winner = 'P' if votes['P'] > votes['B'] else 'B'
        
        # Cálculo de Confiança
        # Se os votos forem muito parecidos (ex: 2.1 vs 2.0), confiança é baixa
        # Se forem distantes (ex: 5.0 vs 1.0), confiança é alta
        
        win_score = votes[winner]
        lose_score = votes['P'] if winner == 'B' else votes['B']
        
        # Fórmula de Probabilidade Sigmoide ajustada
        if win_score > lose_score * 2: prob = 95
        elif win_score > lose_score * 1.5: prob = 85
        elif win_score > lose_score * 1.2: prob = 70
        else: prob = 55
        
        # Override Dragon
        if "DRAGON" in str(reasons): prob = 98

        final_reason = reasons[0] if reasons else (self.strategies['trend']['name'] if w_trend > w_chop else self.strategies['chop']['name'])
        
        return winner, prob, final_reason

# --- SISTEMA DE VISÃO AVANÇADO (HSV + REGIÃO) ---
class VisionSystem:
    def __init__(self):
        self.sct = mss.mss() # Captura rápida
        self.lock = threading.Lock()
        self.targets = {'P': None, 'B': None, 'E': None} # Calibração (HSV)
        
    def get_pixel_avg(self, x, y, size=3):
        """Pega a média de cor numa área de 3x3 ou 5x5 pixels ao redor do mouse."""
        with self.lock:
            monitor = {"top": int(y - size//2), "left": int(x - size//2), "width": size, "height": size}
            try:
                img = self.sct.grab(monitor)
                # Média simples
                r, g, b = 0, 0, 0
                count = 0
                for xx in range(img.width):
                    for yy in range(img.height):
                        p = img.pixel(xx, yy)
                        r += p[0]; g += p[1]; b += p[2]
                        count += 1
                return (int(r/count), int(g/count), int(b/count))
            except:
                return (0,0,0)

    def calibrate(self, key, x, y):
        c = self.get_pixel_avg(x, y)
        h, s, v = colorsys.rgb_to_hsv(c[0]/255, c[1]/255, c[2]/255)
        self.targets[key] = (h, s, v)
        return c

    def identify(self, x, y):
        c = self.get_pixel_avg(x, y) # (R, G, B)
        h, s, v = colorsys.rgb_to_hsv(c[0]/255, c[1]/255, c[2]/255)
        
        # 1. Checa Calibração (Prioridade Máxima)
        best_match = None
        min_dist = 1.0
        
        for key, target in self.targets.items():
            if target is None: continue
            th, ts, tv = target
            
            # Distância baseada primariamente em Matiz (Hue)
            dist_h = min(abs(h - th), 1 - abs(h - th)) # Distância circular
            dist_s = abs(s - ts)
            
            # Score de diferença (menor é melhor)
            score = (dist_h * 2) + (dist_s) 
            
            if score < 0.15: # Threshold de match
                if score < min_dist:
                    min_dist = score
                    best_match = key

        if best_match: return best_match, c, h
        
        # 2. Fallback Ranges (Se não calibrado)
        # Saturação alta necessária para P/B
        if s > 0.3 and v > 0.3:
            if (h < 0.1 or h > 0.9): return 'B', c, h
            if (0.55 < h < 0.70): return 'P', c, h
            if (0.28 < h < 0.42): return 'E', c, h
            
        return None, c, h

# --- INTERFACE MASTER (UI FINAL) ---
class BacBoProV2(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BAC BO - MASTER AI v2.0")
        self.geometry("950x800")
        self.configure(fg_color=C_BG)
        
    # ... inside build_ui ...
        self.lbl_status = ctk.CTkLabel(head, text="SISTEMA AGUARDANDO...", font=("Consolas", 14), text_color="gray")
        self.lbl_status.pack(side="right", padx=10)
        
        self.lbl_streak = ctk.CTkLabel(head, text="🔥 WIN STREAK: 0", font=("Impact", 20), text_color="#FFD700")
        self.lbl_streak.pack(side="right", padx=20)

    # ... inside __init__ ...
        self.scan_pos = None
        self.is_tracking = False
        self.last_res = None
        self.streak = 0
        self.last_predicted_winner = None

    # ... inside add_res ...
    def add_res(self, res):
        # 1. Check if previous prediction was correct
        if self.last_predicted_winner and res != 'E':
            if res == self.last_predicted_winner:
                self.streak += 1
                self.lbl_streak.configure(text=f"🔥 WIN STREAK: {self.streak}", text_color="#00E676") # Green
            else:
                self.streak = 0
                self.lbl_streak.configure(text="💀 WIN STREAK: 0", text_color="#FF5252") # Red
        
        self.brain.add_result(res)
        self.update_view()

    # ... inside update_view ...
            # ...
            # Update Painel Principal
            txt_color = C_PLAYER if winner == 'P' else C_BANKER
            self.lbl_pred_main.configure(text="PLAYER" if winner == 'P' else "BANKER", text_color=txt_color)
            self.bar_conf.set(prob / 100)
            
            # Save for next check
            self.last_predicted_winner = winner
            
            # Cor da barra
            b_col = "#00e676" if prob > 90 else ("#29b6f6" if prob > 70 else "#ffa726")
            self.bar_conf.configure(progress_color=b_col)
            # ...

if __name__ == "__main__":
    app = BacBoProV2()
    app.mainloop()

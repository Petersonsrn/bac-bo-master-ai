import tkinter as tk
from tkinter import messagebox
import pyautogui
import threading
import time
import keyboard
import mss
from baccarat_engine_pro import BaccaratEnginePro

# --- CONFIGURAÇÕES VISUAIS (Aesthetics) ---
COLOR_BG = "#121212"
COLOR_FG = "#FFFFFF"
COLOR_PLAYER = "#2962FF" # Azul Vibrante
COLOR_BANKER = "#D50000" # Vermelho Vibrante
COLOR_TIE = "#00C853"    # Verde
COLOR_PANEL = "#1E1E1E"
FONT_MAIN = ("Segoe UI", 12)
FONT_BIG = ("Segoe UI", 24, "bold")
FONT_HUGE = ("Segoe UI", 48, "bold")

class BaccaratGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GTO BACCARAT DOCTOR (ULTRA EDITION)")
        self.root.geometry("800x650")
        self.root.configure(bg=COLOR_BG)
        
        self.engine = BaccaratEnginePro()
        
        # Audio Alerts
        self.sound_enabled = tk.BooleanVar(value=True)
        
        # Stats Tracker
        self.stats = {'wins': 0, 'losses': 0}
        self.current_prediction = None
        
        # Scanner State
        self.auto_scan_active = False
        self.scan_coords = None
        
        self.setup_ui()

    def get_pixel_mss(self, x, y):
        """Robust pixel reading using MSS (Supports Multi-Monitor)"""
        with mss.mss() as sct:
            # MSS requires top, left, width, height
            # We capture a 1x1 pixel region
            monitor = {"top": int(y), "left": int(x), "width": 1, "height": 1}
            try:
                simg = sct.grab(monitor)
                return simg.pixel(0, 0) # Returns (R, G, B)
            except Exception as e:
                print(f"Erro Vision: {e}")
                return (0, 0, 0)

    def setup_ui(self):
        # --- HEADER & OPTIONS ---
        header_frame = tk.Frame(self.root, bg=COLOR_PANEL, height=50)
        header_frame.pack(fill="x")
        
        lbl_title = tk.Label(header_frame, text="🦁 GTO ANALYTICS HUD", bg=COLOR_PANEL, fg=COLOR_FG, font=("Segoe UI", 14, "bold"))
        lbl_title.pack(side="left", padx=20, pady=10)
        
        # Options Frame (Top Right)
        opts_frame = tk.Frame(header_frame, bg=COLOR_PANEL)
        opts_frame.pack(side="right", padx=10)
        
        # Checkbox Always on Top
        self.top_enabled = tk.BooleanVar(value=True)
        chk_top = tk.Checkbutton(opts_frame, text="Fixar no Topo", var=self.top_enabled, command=self.toggle_top, bg=COLOR_PANEL, fg="white", selectcolor="#333", activebackground=COLOR_PANEL, activeforeground="white")
        chk_top.pack(side="left", padx=5)
        
        # Force focus
        self.root.lift()
        self.root.attributes("-topmost", True)
        
        # Checkbox Som
        chk_sound = tk.Checkbutton(opts_frame, text="Sons", var=self.sound_enabled, bg=COLOR_PANEL, fg="white", selectcolor="#333", activebackground=COLOR_PANEL, activeforeground="white")
        chk_sound.pack(side="left", padx=5)

        # Labels de Segurança
        lbl_safe = tk.Label(header_frame, text="🔒 MODO PASSIVO (SEM CLIQUES)", bg=COLOR_PANEL, fg="#00E676", font=("Segoe UI", 8))
        lbl_safe.pack(side="right", padx=10)
        
        # Strategy Toggle
        self.strategy_mode = tk.BooleanVar(value=True) # True=Surf (Favor), False=Contra (Reversal)
        chk_strat = tk.Checkbutton(opts_frame, text="Modo Surf 🏄", var=self.strategy_mode, command=self.update_view, bg=COLOR_PANEL, fg="#00E5FF", selectcolor="#333", activebackground=COLOR_PANEL, activeforeground="#00E5FF")
        chk_strat.pack(side="left", padx=5)

        # --- PREDICTION AREA (Main Focus) ---
        self.pred_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.pred_frame.pack(pady=10, fill="x")
        
        self.lbl_sinal = tk.Label(self.pred_frame, text="AGUARDANDO INÍCIO...", bg=COLOR_BG, fg="#555555", font=FONT_BIG)
        self.lbl_sinal.pack()
        
        self.lbl_razao = tk.Label(self.pred_frame, text="Inicie o histórico para previsão", bg=COLOR_BG, fg="#AAAAAA", font=("Segoe UI", 11, "italic"))
        self.lbl_razao.pack()

        # Stats Visualizer
        self.lbl_stats = tk.Label(self.pred_frame, text="📊 PLACAR: 0 ✅  -  0 ❌  (0%)", bg=COLOR_BG, fg="#FFC107", font=("Consolas", 14, "bold"))
        self.lbl_stats.pack(pady=10)

        # --- HISTORY VISUALIZATION (Simple Grid) ---
        self.history_frame = tk.Frame(self.root, bg=COLOR_PANEL, bd=1, relief="flat")
        self.history_frame.pack(pady=5, padx=20, fill="both", expand=True)
        
        self.canvas = tk.Canvas(self.history_frame, bg="#252526", height=180, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # --- POWER BAR ---
        self.canvas_bar = tk.Canvas(self.root, bg=COLOR_BG, height=30, highlightthickness=0)
        self.canvas_bar.pack(pady=5)

        # --- CONTROLS ---
        controls_frame = tk.Frame(self.root, bg=COLOR_BG)
        controls_frame.pack(pady=10, side="bottom", fill="x")

        # Buttons style
        btn_params = {'font': FONT_BIG, 'fg': 'white', 'bd': 0, 'activeforeground': 'white'}
        
        self.btn_player = tk.Button(controls_frame, text="P", bg=COLOR_PLAYER, activebackground="#0039Cb", command=lambda: self.add_result('P'), width=4, **btn_params)
        self.btn_player.pack(side="left", padx=20, pady=10)
        
        self.btn_scan = tk.Button(controls_frame, text="👁️ SCAN", bg="#FF9800", activebackground="#F57C00", command=self.start_scan_thread, font=("Segoe UI", 12, "bold"), width=12)
        self.btn_scan.pack(side="left", padx=10)
        
        self.btn_auto_scan = tk.Button(controls_frame, text="🤖 MAPEAR PLACAR (OFF)", bg="#546E7A", activebackground="#455A64", command=self.toggle_auto_scan, font=("Segoe UI", 10, "bold"), width=15)
        self.btn_auto_scan.pack(side="left", padx=5)

        self.btn_snap = tk.Button(controls_frame, text="📸", bg="#4527A0", fg="white", command=self.take_snapshot, font=("Segoe UI", 12), width=4, bd=0)
        self.btn_snap.pack(side="left", padx=5)
        
        self.btn_banker = tk.Button(controls_frame, text="B", bg=COLOR_BANKER, activebackground="#9B0000", command=lambda: self.add_result('B'), width=4, **btn_params)
        self.btn_banker.pack(side="right", padx=20, pady=10)

    def take_snapshot(self):
        try:
            ts = int(time.time())
            fname = f"debug_view_{ts}.png"
            pyautogui.screenshot(fname)
            self.lbl_razao.config(text=f"📸 Foto salva: {fname}")
            # Log coordinates if active
            if self.map_coords:
                print(f"COORDS: {self.map_coords}")
        except Exception as e:
            print(e)
        
        # Undo e Reset
        mini_controls = tk.Frame(self.root, bg=COLOR_BG)
        mini_controls.pack(side="bottom", pady=5)
        
        tk.Button(mini_controls, text="Desfazer (Undo)", command=self.undo, bg="#424242", fg="white", bd=0).pack(side="left", padx=5)
        tk.Button(mini_controls, text="Resetar Mesa", command=self.reset, bg="#424242", fg="white", bd=0).pack(side="left", padx=5)
        tk.Button(mini_controls, text="💾 Salvar Session", command=self.save_session, bg="#2E7D32", fg="white", bd=0).pack(side="left", padx=5)

        # Keyboard Shortcuts
        self.root.bind('<Left>', lambda e: self.add_result('P'))
        self.root.bind('<Right>', lambda e: self.add_result('B'))
        self.root.bind('<space>', lambda e: self.start_scan_thread())

    def toggle_top(self):
        self.root.attributes("-topmost", self.top_enabled.get())

    def save_session(self):
        self.engine.export_csv()
        messagebox.showinfo("Salvo", "Histórico salvo em 'sessao_baccarat.csv'!")

    def beep_alert(self):
        if self.sound_enabled.get():
            try:
                import winsound
                winsound.Beep(1000, 200) # Frequencia 1000Hz, 200ms
            except:
                pass

    def add_result(self, res):
        # 1. Valida Previsão Anterior (Win/Loss Check)
        if hasattr(self, 'current_prediction') and self.current_prediction:
            target = self.current_prediction
            if res != 'E': # Ignora empates para estatística
                if res == target:
                    self.stats['wins'] += 1
                else:
                    self.stats['losses'] += 1
        
        self.engine.add_result(res)
        self.update_view()

    def undo(self):
        if self.engine.raw_history:
            self.engine.raw_history.pop()
            self.update_view()

    def reset(self):
        self.engine.raw_history = []
        self.stats = {'wins': 0, 'losses': 0}
        self.current_prediction = None
        self.update_view()

    def update_view(self):
        self.canvas.delete("all")
        # Grid Drawing Logic (Mantida e ajustada)
        x_start, y_start, radius = 10, 20, 12
        spacing_x, spacing_y = 30, 30
        
        visible_hist = self.engine.raw_history[-60:] if len(self.engine.raw_history) > 60 else self.engine.raw_history
        cols = 0
        rows = 0
        for res in visible_hist:
            color = COLOR_PLAYER if res == 'P' else (COLOR_BANKER if res == 'B' else COLOR_TIE)
            x = x_start + (cols * spacing_x)
            y = y_start + (rows * spacing_y)
            self.canvas.create_oval(x, y, x+radius*2, y+radius*2, fill=color, outline=color)
            self.canvas.create_text(x+radius, y+radius, text=res, fill="white", font=("Arial", 8, "bold"))
            rows += 1
            if rows >= 5: cols += 1; rows = 0

        # Stats Update
        # ... logic for stats visual (optional)

        # Predict Update
        sinal, razao = self.engine.predict_advanced()
        
        # Inversion Logic (Strategy Mode)
        if not self.strategy_mode.get() and sinal:
             # Inverte o sinal
             sinal = 'B' if sinal == 'P' else 'P'
             razao = f"[MODO CONTRA] Apostando na Quebra de {razao}"
             
             # Inverte probabilidade Monte Carlo (Visual apenas)
             probs = getattr(self.engine, 'last_mc_probs', (50, 50))
             # Swap (P, B) -> (B, P)
             self.engine.last_mc_probs = (probs[1], probs[0])

        # GUARDA A PREVISÃO ATUAL (PARA CONFERIR O RESULTADO NA PRÓXIMA)
        self.current_prediction = sinal
        
        # Update Stats Label
        total_games = self.stats['wins'] + self.stats['losses']
        acc = int((self.stats['wins']/total_games)*100) if total_games > 0 else 0
        self.lbl_stats.config(text=f"📊 PLACAR: {self.stats['wins']} ✅  -  {self.stats['losses']} ❌  ({acc}%)")

        if sinal:
            # Play sound if new signal appears
            if self.lbl_sinal.cget("text") == "EM ANÁLISE...":
                self.beep_alert()
                
            probs = getattr(self.engine, 'last_mc_probs', (50, 50))
            p_pct, b_pct = probs
            
            bar_len = 300
            p_width = int((p_pct / 100) * bar_len)
            
            self.canvas_bar.delete("all")
            self.canvas_bar.create_rectangle(0, 0, bar_len, 20, fill=COLOR_BANKER, width=0)
            self.canvas_bar.create_rectangle(0, 0, p_width, 20, fill=COLOR_PLAYER, width=0)
            self.canvas_bar.create_text(10, 10, text=f"P: {int(p_pct)}%", anchor="w", fill="white", font=("Arial", 9, "bold"))
            self.canvas_bar.create_text(bar_len-10, 10, text=f"B: {int(b_pct)}%", anchor="e", fill="white", font=("Arial", 9, "bold"))
            
            if sinal == 'P':
                self.lbl_sinal.config(text=f"🔵 APOSTAR: PLAYER", fg="white", bg=COLOR_PLAYER, font=("Segoe UI", 32, "bold"))
            else:
                self.lbl_sinal.config(text=f"🔴 APOSTAR: BANKER", fg="white", bg=COLOR_BANKER, font=("Segoe UI", 32, "bold"))
            self.lbl_razao.config(text=f"{razao}\n(Confiança: {max(p_pct, b_pct)}%)")
        else:
            self.canvas_bar.delete("all")
            self.lbl_sinal.config(text="EM ANÁLISE...", fg="#555555", bg=COLOR_BG, font=FONT_BIG)
            self.lbl_razao.config(text="Aguardando dados da leitura...")

    def start_scan_thread(self):
        # Scan Rápido (0.3s)
        threading.Thread(target=self.scan_screen, daemon=True).start()

    # --- MONITORAMENTO MULTI-PONTO (Placar) ---
    def toggle_auto_scan(self):
        # Defensive init check
        if not hasattr(self, 'auto_scan_active'): self.auto_scan_active = False

        # Agora funciona como "Mapear Placar"
        if self.auto_scan_active:
            self.auto_scan_active = False
            self.btn_auto_scan.config(text="🤖 MAPEAR PLACAR (OFF)", bg="#546E7A")
            return

        self.mapping_step = 0
        self.map_coords = {} # {'P': (x,y), 'B': (x,y), 'T': (x,y)}
        self.map_colors = {} # Cores de referência
        
        messagebox.showinfo("Configuração de Visão", 
            "Vamos ensinar o bot a olhar o PLACAR (os quadrados coloridos com números).\n\n"
            "1. Vou pedir para você apontar para o AZUL, depois VERMELHO, depois EMPATE.\n"
            "2. Você terá 3 segundos para cada um.\n\n"
            "Clique OK para começar!")
            
        self.lbl_razao.config(text="⏳ Aponte para o PLACAR AZUL (Jogador)...")
        self.root.after(3000, lambda: self.save_map_point('P'))

    def save_map_point(self, type_):
        x, y = pyautogui.position()
        c = self.get_pixel_mss(x, y)
        print(f"Calibrado {type_} em ({x},{y}) -> Cor: {c}")
        self.map_coords[type_] = (x, y)
        self.map_colors[type_] = c
        self.beep_alert()
        
        if type_ == 'P':
            self.lbl_razao.config(text=f"✅ Azul salvo! Agora aponte para o PLACAR VERMELHO (Banca)...")
            self.root.after(3000, lambda: self.save_map_point('B'))
        elif type_ == 'B':
            self.lbl_razao.config(text=f"✅ Vermelho salvo! Agora aponte para o MEIO (Empate/Dourado)...")
            self.root.after(3000, lambda: self.save_map_point('T'))
        elif type_ == 'T':
            self.lbl_razao.config(text="✅ Configuração Concluída! Monitorando...")
            self.auto_scan_active = True
            self.btn_auto_scan.config(text="🟢 VISÃO ATIVA", bg="#00E676")
            threading.Thread(target=self.multi_point_scan, daemon=True).start()

    def multi_point_scan(self):
        last_result = None
        
        while self.auto_scan_active:
            if keyboard.is_pressed('esc'):
                self.toggle_auto_scan()
                break
                
            # Verifica os 3 pontos
            # Verifica os 3 pontos usando DELTA (Mudança de Cor)
            try:
                # Player
                px, py = self.map_coords['P']
                pc = self.get_pixel_mss(px, py)
                bp = self.map_colors['P'] # Cor Base (Salva no Mapeamento)
                # Calcula diferença (Delta)
                delta_p = abs(pc[0]-bp[0]) + abs(pc[1]-bp[1]) + abs(pc[2]-bp[2])
                is_p_active = delta_p > 50
                
                # Banker
                bx, by = self.map_coords['B']
                bc = self.get_pixel_mss(bx, by)
                bb = self.map_colors['B']
                delta_b = abs(bc[0]-bb[0]) + abs(bc[1]-bb[1]) + abs(bc[2]-bb[2])
                is_b_active = delta_b > 50
                
                # Tie (Threshold ALTÍSSIMO para matar ruído)
                tx, ty = self.map_coords['T']
                tc = self.get_pixel_mss(tx, ty)
                bt = self.map_colors['T']
                delta_t = abs(tc[0]-bt[0]) + abs(tc[1]-bt[1]) + abs(tc[2]-bt[2])
                is_t_active = delta_t > 100
                
                detected = None
                
                # Debug Info
                debug_txt = f"ΔP:{delta_p} ΔB:{delta_b} ΔT:{delta_t}"
                
                # Lógica de Decisão Baseada no MAIOR Delta (Quem piscou mais forte?)
                # Isso impede que um Empate 'ruído' (36) bloqueie um Player 'Flash' (200)
                
                deltas = {'P': delta_p, 'B': delta_b, 'E': delta_t}
                max_delta = max(deltas.values())
                
                detected = None
                
                # Threshold Global (mínimo para qualquer detecção)
                min_threshold = 50
                
                if max_delta > min_threshold:
                    # Descobre quem tem o maior delta
                    # Tie precisa vencer o threshold de 100 E ser o maior
                    if max_delta == delta_t and max_delta > 100:
                        detected = 'E'
                        debug_txt = f"DET: EMPATE (Δ {max_delta})"
                    elif max_delta == delta_p and delta_p > 50:
                        detected = 'P'
                        debug_txt = f"DET: PLAYER (Δ {max_delta})"
                    elif max_delta == delta_b and delta_b > 50:
                        detected = 'B'
                        debug_txt = f"DET: BANKER (Δ {max_delta})"
                else:
                    debug_txt = f"Monitorando... (Δ Max: {max_delta})"
                    last_result = None

                self.root.after(0, lambda: self.lbl_razao.config(text=f"👁️ {debug_txt}", font=("Segoe UI", 9)))
                
                # Disparo (Só adiciona se mudou de 'Nada' para 'Algo', ou mudou o resultado)
                # Como resetamos last_result=None quando apaga, isso permite sequencias P -> Nada -> P
                if detected and detected != last_result:
                     self.root.after(0, lambda r=detected: self.add_result(r))
                     self.beep_alert()
                     last_result = detected
                     time.sleep(5) # Delay para evitar leitura dupla do mesmo flash

            except Exception as e:
                print(f"Erro scan: {e}")
                
            time.sleep(0.2)

    def scan_screen(self):
        # Instant Scan using MSS
        self.lbl_razao.config(text="LENDO COR SOB O MOUSE...")
        time.sleep(0.3) 
        
        x, y = pyautogui.position()
        cor = self.get_pixel_mss(x, y)
        
        r, g, b = cor
        print(f"Scan Manual em ({x},{y}): {cor}")
        
        # Mais tolerante: Detectar Vermelho Forte ou Azul Forte
        res = None
        
        # Banker: R muito maior que G e B
        if r > 100 and r > g + 30 and r > b + 30: 
            res = 'B'
            
        # Player: B muito maior que R e G
        elif b > 100 and b > r + 30 and b > g + 30: 
            res = 'P'
            
        # Tie: G alto (Verde ou Dourado às vezes tem G e R altos)
        elif g > 100 and g > b + 20: 
            res = 'E'
        
        if res:
            self.root.after(0, lambda: self.add_result(res))
            self.root.after(0, lambda: self.lbl_razao.config(text=f"Scan: {res} Detectado ({r},{g},{b})"))
        else:
            self.root.after(0, lambda: self.lbl_razao.config(text=f"Scan Incerto: ({r},{g},{b})"))

    def toggle_vision_debug(self):
        # Ativa/Desativa modo debug visual
        if not hasattr(self, 'debug_active'): self.debug_active = False
        self.debug_active = not self.debug_active
        
        if self.debug_active:
             threading.Thread(target=self.vision_debugger_loop, daemon=True).start()
             self.btn_debug.config(bg="#FF5252", text="DEBUG ON")
        else:
             self.btn_debug.config(bg="#424242", text="🐛 DEBUG")

    def vision_debugger_loop(self):
        while self.debug_active:
             x, y = pyautogui.position()
             c = self.get_pixel_mss(x, y)
             msg = f"MOUSE: ({x}, {y}) | COR: {c}"
             
             # Atualiza UI
             self.root.after(0, lambda: self.lbl_razao.config(text=msg))
             time.sleep(0.1)

if __name__ == "__main__":
    root = tk.Tk()
    app = BaccaratGUI(root)
    
    # Add debug button to footer
    app.btn_debug = tk.Button(root, text="🐛 DEBUG", command=app.toggle_vision_debug, bg="#424242", fg="white", bd=0)
    app.btn_debug.place(x=10, y=620) # Floating bottom left logic
    
    root.mainloop()

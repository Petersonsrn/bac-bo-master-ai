import customtkinter as ctk
import pyautogui
import threading
import time
import keyboard
import mss
import colorsys
from baccarat_engine_pro import BaccaratEnginePro

# --- SETUP TEMA ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# --- CORES ADAPTATIVAS ---
COLOR_PLAYER = "#3B8ED0" # Azul Moderno
COLOR_BANKER = "#E04F5F" # Vermelho Moderno
COLOR_TIE = "#2CC985"    # Verde Suave
COLOR_DARK = "#1A1A1A"
COLOR_GLASS = "#2B2B2B"

class CyborgBaccaratApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BAC BO - CYBORG PREDICTOR PRO (v5.0 Auto-Aim)")
        self.geometry("900x780")
        
        # OTIMIZAÇÃO: Persistência
        self.sct = mss.mss()
        self.files_lock = threading.Lock()
        
        self.engine = BaccaratEnginePro()
        self.stats = {'wins': 0, 'losses': 0}
        self.current_prediction = None
        
        # Auto-Scan Variables
        self.last_scan_coords = None
        self.last_detected_result = None
        
        # VARIAVEIS
        self.var_confidence = ctk.DoubleVar(value=0.0)
        self.toggles = {
            'sound': ctk.BooleanVar(value=True),
            'vision_mode': ctk.StringVar(value="COMPATIVEL"), 
            'auto_track': ctk.BooleanVar(value=False)
        }

        # Calibration Data
        self.calibration = {} # {'P': (h,s,v), 'B': (h,s,v), 'E': (h,s,v)}
        
        self.setup_ui()
        self.attributes("-topmost", True)
        
        # KEYBINDS
        self.bind('<Left>', lambda e: self.register_result('P'))
        self.bind('<Right>', lambda e: self.register_result('B'))
        self.bind('<Up>', lambda e: self.register_result('E'))
        self.bind('<space>', lambda e: self.scan_once())
        # Calibration Hotkeys
        self.bind('<F1>', lambda e: self.calibrate_target('P'))
        self.bind('<F2>', lambda e: self.calibrate_target('B'))
        self.bind('<F3>', lambda e: self.calibrate_target('E'))

    def get_pixel(self, x, y):
        """
        Sistema de Visão Híbrido:
        - MSS: Rápido, mas pode falhar com Scale do Windows (125%, 150%)
        - PIL/PyAutoGUI: Mais lento, mas respeita a escala do SO.
        """
        mode = self.toggles['vision_mode'].get()
        
        if mode == "RAPIDO (MSS)":
            with self.files_lock:
                monitor = {"top": int(y), "left": int(x), "width": 1, "height": 1}
                try: 
                    # MSS retorna BGRA, precisamos converter para RGB
                    bgra = self.sct.grab(monitor).pixel(0, 0)
                    return (bgra[0], bgra[1], bgra[2])
                except: return (0,0,0)
        else:
            # Modo Compatível (Safe)
            try:
                return pyautogui.pixel(x, y)
            except:
                return (0,0,0)

    def calibrate_target(self, target):
        x, y = pyautogui.position()
        c = self.get_pixel(x, y)
        r, g, b = c
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        self.calibration[target] = (h, s, v)
        self.msg_toast(f"🎯 COR {target} CALIBRADA!")
        self.lbl_debug.configure(text=f"CALIBRADO {target}: H={h:.2f} S={s:.2f}")

    def scan_once(self):
        # ...
        x, y = pyautogui.position()
        self.last_scan_coords = (x, y)
        self.process_scan(x, y, auto=False)

    def process_scan(self, x, y, auto=False):
        c = self.get_pixel(x, y)
        r, g, b = c
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        if not auto: 
             try: self.color_box.configure(fg_color=f"#{r:02x}{g:02x}{b:02x}")
             except: pass

        res = None
        
        # 1. Check Calibration Matches (High Priority)
        for target, cal_hsv in self.calibration.items():
            ch, cs, cv = cal_hsv
            # Tolerância: Hue 0.05, Saturation 0.2, Value 0.2
            if abs(h - ch) < 0.08 and abs(s - cs) < 0.25:
                res = target
                break
        
        # 2. Default Ranges (Fallback)
        if not res and s > 0.2 and v > 0.2:
            if (h < 0.1 or h > 0.9): res = 'B'
            elif (0.55 < h < 0.75): res = 'P'
            elif (0.25 < h < 0.45): res = 'E'
            
        # 3. Brightness Fallback
        if not res and v > 0.8:
            if r > g+20 and r > b+20: res = 'B'
            elif b > r+20 and b > g+20: res = 'P'

        # Logic
        if res:
            if auto:
                if res != self.last_detected_result:
                    time.sleep(0.5) # Debounce
                    # ... simple recheck logic meant for speed ...
                    self.register_result(res)
                    self.last_detected_result = res
            else:
                self.register_result(res)
                self.last_detected_result = res
                
            self.lbl_debug.configure(text=f"Scan: {res} (H:{h:.2f}) {'[Calib]' if self.calibration else ''}")
        else:
            if not auto: self.lbl_debug.configure(text=f"Scan FALHOU (H:{h:.2f}) - Use F1/F2 p/ Calibrar")
     
    # ... setup_ui changes ...
    # Add calibration info label or buttons in footer
    # ...
    
    def msg_toast(self, text):
        self.lbl_main_signal.configure(text=text, font=("Arial", 20))
        self.after(2000, self.update_prediction) # Restore after 2s
        """
        Sistema de Visão Híbrido:
        - MSS: Rápido, mas pode falhar com Scale do Windows (125%, 150%)
        - PIL/PyAutoGUI: Mais lento, mas respeita a escala do SO.
        """
        mode = self.toggles['vision_mode'].get()
        
        if mode == "RAPIDO (MSS)":
            with self.files_lock:
                monitor = {"top": int(y), "left": int(x), "width": 1, "height": 1}
                try: return self.sct.grab(monitor).pixel(0, 0)
                except: return (0,0,0)
        else:
            # Modo Compatível (Safe)
            try:
                return pyautogui.pixel(x, y)
            except:
                return (0,0,0)

    def setup_ui(self):
        # 1. HEADER
        self.header = ctk.CTkFrame(self, height=80, fg_color="transparent")
        self.header.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(self.header, text="CYBORG PREDICTOR", font=("Orbitron", 24, "bold"), text_color="white").pack(side="left")
        ctk.CTkLabel(self.header, text="v5.0 Auto-Aim", font=("Arial", 10), text_color="#00E676").pack(side="left", padx=5, pady=(10,0))
        
        self.fr_stats = ctk.CTkFrame(self.header, fg_color="#212121", corner_radius=10)
        self.fr_stats.pack(side="right")
        self.lbl_stats = ctk.CTkLabel(self.fr_stats, text="0W - 0L (0%)", font=("Consolas", 20, "bold"), text_color="#FBC02D")
        self.lbl_stats.pack(padx=20, pady=5)

        # 2. MAIN RING
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(fill="both", expand=True, padx=20)
        
        self.ring_frame = ctk.CTkFrame(self.main_area, fg_color="#151515", corner_radius=20, border_width=2, border_color="#333")
        self.ring_frame.pack(fill="both", expand=True, pady=10)
        
        self.lbl_main_signal = ctk.CTkLabel(self.ring_frame, text="PRONTO", font=("Arial Black", 48), text_color="#555")
        self.lbl_main_signal.place(relx=0.5, rely=0.4, anchor="center")
        
        self.lbl_sub_reason = ctk.CTkLabel(self.ring_frame, text="Mire e aperte ESPAÇO", font=("Arial", 16), text_color="#888")
        self.lbl_sub_reason.place(relx=0.5, rely=0.6, anchor="center")
        
        self.progress_conf = ctk.CTkProgressBar(self.ring_frame, variable=self.var_confidence, width=400, height=15)
        self.progress_conf.place(relx=0.5, rely=0.75, anchor="center")

        # 3. BEAD PLATE
        self.hist_scroll = ctk.CTkScrollableFrame(self, height=100, orientation="horizontal", label_text="HISTÓRICO")
        self.hist_scroll.pack(fill="x", padx=20, pady=5)
        self.hist_container = ctk.CTkFrame(self.hist_scroll, fg_color="transparent")
        self.hist_container.pack(fill="both", expand=True)

        # 4. FOOTER
        self.footer = ctk.CTkFrame(self, height=160, fg_color="#181818")
        self.footer.pack(fill="x", side="bottom")
        
        # -- Controls --
        btn_opts = {'width': 80, 'height': 60, 'font': ("Arial", 18, "bold"), 'corner_radius': 15}
        ctk.CTkButton(self.footer, text="PLAYER", command=lambda: self.register_result('P'), fg_color=COLOR_PLAYER, **btn_opts).pack(side="left", padx=20, pady=20)
        ctk.CTkButton(self.footer, text="BANKER", command=lambda: self.register_result('B'), fg_color=COLOR_BANKER, **btn_opts).pack(side="right", padx=20, pady=20)
        
        mid_frame = ctk.CTkFrame(self.footer, fg_color="transparent")
        mid_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Botão Scan Grande
        ctk.CTkButton(mid_frame, text="DEFINIR MIRA (Espaço)", command=self.scan_once, fg_color="#FB8C00", font=("Arial", 12, "bold")).pack(fill="x", pady=2)
        
        # Auto-Track Switch
        self.sw_auto = ctk.CTkSwitch(mid_frame, text="RASTREIO AUTO (Mira Fixa)", variable=self.toggles['auto_track'], command=self.toggle_auto_track, progress_color="#00E676")
        self.sw_auto.pack(fill="x", pady=5)

        # Undo / Reset Row
        ur_frame = ctk.CTkFrame(mid_frame, fg_color="transparent")
        ur_frame.pack(fill="x", pady=2)
        ctk.CTkButton(ur_frame, text="↩️", command=self.undo_last, fg_color="#444", width=40).pack(side="left", padx=2, expand=True, fill="x")
        ctk.CTkButton(ur_frame, text="🗑️", command=self.reset_all, fg_color="#D32F2F", width=40).pack(side="right", padx=2)
        
        # Options Row
        opt_frame = ctk.CTkFrame(mid_frame, fg_color="transparent")
        opt_frame.pack(fill="x", pady=2)
        
        ctk.CTkSwitch(opt_frame, text="Som", variable=self.toggles['sound']).pack(side="left", padx=5)
        ctk.CTkOptionMenu(opt_frame, variable=self.toggles['vision_mode'], values=["RAPIDO (MSS)", "COMPATIVEL"], width=100).pack(side="right", padx=5)
        ctk.CTkButton(opt_frame, text="DEBUG", command=self.toggle_debug, width=60, fg_color="#444").pack(side="right", padx=5)

        # Help Label
        ctk.CTkLabel(mid_frame, text="Calibrar: F1=Azul | F2=Verm | F3=Empate", font=("Arial", 10), text_color="#666").pack(side="bottom", pady=2)

        # Visualizador de Cor (Color Box)
        self.color_box = ctk.CTkLabel(self.footer, text="", width=40, height=40, fg_color="black", corner_radius=5)
        self.color_box.place(relx=0.5, rely=0.9, anchor="center") # Centralizado embaixo

        self.lbl_debug = ctk.CTkLabel(self.footer, text="Sistema Iniciado", font=("Consolas", 10), text_color="gray")
        self.lbl_debug.place(x=10, y=5)

    def toggle_top(self): pass # Deprecated in new layout

    def update_history_view(self):
        for widget in self.hist_container.winfo_children(): widget.destroy()
        hist = self.engine.raw_history.copy()
        
        # --- GHOST BEAD (O Possível Final) ---
        # Adiciona a previsão atual como um 'fantasma' no futuro
        if self.current_prediction:
            hist.append(self.current_prediction)
            
        if not hist: return
        
        # Mostra os últimos 30 (incluindo o fantasma)
        # Inverte para mostrar o mais recente na esquerda (ou direita? padrão é esquerda p/ direita em scroll)
        # Vamos manter o padrão ocidental: Esquerda=Antigo, Direita=Novo (Futuro)
        # O código original usava reversed() e pack(side=left), ou seja:
        # [Novo] [Velho] [Velho] ...
        # Isso é confuso. Vamos mudar para:
        # ... [Velho] [Velho] [Novo] [FANTASMA] -> Fluido do tempo correto.
        
        recent = hist[-30:] # Pega os 30 mais recentes
        
        for i, res in enumerate(recent):
            is_ghost = (self.current_prediction and i == len(recent) - 1)
            
            if res == 'P': c, txt = COLOR_PLAYER, "P"
            elif res == 'B': c, txt = COLOR_BANKER, "B"
            else: c, txt = COLOR_TIE, "E"
            
            if is_ghost:
                # Estilo Diferenciado para o Futuro
                btn = ctk.CTkButton(self.hist_container, text="🔮", width=40, height=40, corner_radius=20, 
                                  fg_color="transparent", border_width=2, border_color=c, 
                                  text_color=c, font=("Arial", 16, "bold"))
            else:
                # Estilo Normal
                btn = ctk.CTkButton(self.hist_container, text=txt, width=35, height=35, corner_radius=18, 
                                  fg_color=c, state="disabled", text_color="white", font=("Arial", 12, "bold"))
            
            btn.pack(side="left", padx=2)
            
        # Auto-scroll para o fim (direita) se possível, mas em pack(side=left) o container cresce.
        # O usuário vê o começo. Vamos inverter para pack(side=RIGHT) para que o NOVO apareça no canto?
        # Não, vamos deixar side=left, mas garantir que o usuário entenda a ordem.
        
    def undo_last(self):
        if self.engine.raw_history:
            removed = self.engine.raw_history.pop()
            self.lbl_debug.configure(text=f"Desfeito: {removed}")
            self.update_history_view()
            self.update_prediction()
            # Nota: Stats não são revertidos perfeitamente para simplificar, 
            # mas o fluxo do bot volta ao normal.

    def reset_all(self):
        self.engine.raw_history = []
        self.stats = {'wins': 0, 'losses': 0}
        self.update_history_view()
        self.update_stats()
        self.update_prediction()
        self.lbl_debug.configure(text="SISTEMA RESETADO")
        self.last_detected_result = None # Reset tracker too

    def register_result(self, res):
        if self.current_prediction and res != 'E':
            if res == self.current_prediction:
                self.stats['wins'] += 1
            else:
                self.stats['losses'] += 1
        self.engine.add_result(res)
        self.update_history_view()
        self.update_prediction()
        self.update_stats()

    def update_stats(self):
        total = self.stats['wins'] + self.stats['losses']
        rate = int((self.stats['wins']/total)*100) if total > 0 else 0
        self.lbl_stats.configure(text=f"{self.stats['wins']}W - {self.stats['losses']}L ({rate}%)")

    def update_prediction(self):
        # Unpack 3 values now
        try:
            sinal, prob, reason = self.engine.predict_advanced()
        except ValueError:
            # Fallback for old version compatibility if reload fails
            res = self.engine.predict_advanced()
            if len(res) == 2: 
                sinal, reason = res
                prob = 50
            else:
                sinal, prob, reason = res
        
        if sinal == 'P':
            self.lbl_main_signal.configure(text="PLAYER", text_color=COLOR_PLAYER)
            self.ring_frame.configure(border_color=COLOR_PLAYER)
        elif sinal == 'B':
            self.lbl_main_signal.configure(text="BANKER", text_color=COLOR_BANKER)
            self.ring_frame.configure(border_color=COLOR_BANKER)
        else:
            self.lbl_main_signal.configure(text="AGUARDE", text_color="#777")
            self.ring_frame.configure(border_color="#333")
            prob = 0
            
        # Formata o texto com a probabilidade
        if prob > 0:
            full_text = f"CHANCE: {prob}% | {reason}"
        else:
            full_text = reason or "Aguardando dados..."
            
        self.lbl_sub_reason.configure(text=full_text)
        self.current_prediction = sinal
        
        # Update Confidence Bar
        self.var_confidence.set(prob / 100.0)
        
        # Dynamic Color for Confidence
        if prob >= 90: self.progress_conf.configure(progress_color="#00E676") # Super Green
        elif prob >= 70: self.progress_conf.configure(progress_color="#00B0FF") # Blue
        elif prob >= 50: self.progress_conf.configure(progress_color="#FFEA00") # Yellow
        else: self.progress_conf.configure(progress_color="#FF1744") # Red
        
    def toggle_auto_track(self):
        if self.toggles['auto_track'].get():
            if not self.last_scan_coords:
                self.lbl_debug.configure(text="⚠️ Defina a MIRA com ESPAÇO primeiro!")
                self.toggles['auto_track'].set(False)
                return
            threading.Thread(target=self.auto_scan_loop, daemon=True).start()
            self.lbl_debug.configure(text="RASTREIO ATIVADO 👁️")
        else:
            self.lbl_debug.configure(text="RASTREIO PARADO 🛑")

    def auto_scan_loop(self):
        while self.toggles['auto_track'].get():
            if not self.last_scan_coords: break
            
            x, y = self.last_scan_coords
            self.process_scan(x, y, auto=True)
            time.sleep(2) # Verifica a cada 2 segundos

    def scan_once(self):
        x, y = pyautogui.position()
        self.last_scan_coords = (x, y) # Salva mira
        self.process_scan(x, y, auto=False)

    def process_scan(self, x, y, auto=False):
        c = self.get_pixel(x, y)
        r, g, b = c
        
        # Atualiza Cor Visual
        if not auto: 
             try: self.color_box.configure(fg_color=f"#{r:02x}{g:02x}{b:02x}")
             except: pass

        # ANALISE HSV 🧠 (Muito mais precisa)
        # Normalize RGB values to [0, 1]
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        # HUE Ranges:
        # Red: 0.0-0.1 OR 0.9-1.0
        # Blue: 0.55-0.75
        # Green (Tie): 0.25-0.45
        
        res = None
        
        # Filtro de Saturação/Brilho (Ignora cinza/preto)
        if s > 0.2 and v > 0.2:
            if (h < 0.1 or h > 0.9): res = 'B'
            elif (0.55 < h < 0.75): res = 'P'
            elif (0.25 < h < 0.45): res = 'E'
            
        # Fallback RGB para cores muito brilhantes (quase branco)
        if not res and v > 0.8:
            if r > g+20 and r > b+20: res = 'B'
            elif b > r+20 and b > g+20: res = 'P'

        # Lógica de Disparo
        if res:
            # Em modo Auto, só registra se mudou (Evita duplicados)
            if auto:
                if res != self.last_detected_result:
                    # Delayzinho pra confirmar (debounce)
                    time.sleep(0.5)
                    c2 = self.get_pixel(x, y) # Recheck
                    r2, g2, b2 = c2
                    h2, s2, v2 = colorsys.rgb_to_hsv(r2/255, g2/255, b2/255)
                    
                    # Re-evaluate with the new color
                    recheck_res = None
                    if s2 > 0.2 and v2 > 0.2:
                        if (h2 < 0.1 or h2 > 0.9): recheck_res = 'B'
                        elif (0.55 < h2 < 0.75): recheck_res = 'P'
                        elif (0.25 < h2 < 0.45): recheck_res = 'E'
                    if not recheck_res and v2 > 0.8:
                        if r2 > g2+20 and r2 > b2+20: recheck_res = 'B'
                        elif b2 > r2+20 and b2 > g2+20: recheck_res = 'P'

                    if recheck_res == res: # Se a cor persistiu e o resultado é o mesmo
                         self.register_result(res)
                         self.last_detected_result = res
            else:
                self.register_result(res)
                self.last_detected_result = res
                
            self.lbl_debug.configure(text=f"Scan ({'Auto' if auto else 'Manual'}): {res} (H:{h:.2f})")
        else:
            if not auto: self.lbl_debug.configure(text=f"Scan FALHOU (H:{h:.2f} S:{s:.2f})")

    def toggle_debug(self):
        if not hasattr(self, 'debug_active'): self.debug_active = False
        self.debug_active = not self.debug_active
        if self.debug_active: threading.Thread(target=self.debug_loop, daemon=True).start()

    def debug_loop(self):
        while self.debug_active:
             x, y = pyautogui.position()
             c = self.get_pixel(x, y)
             r,g,b = c
             h,s,v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
             
             t = f"POS:{x},{y} | RGB:{c} | HSV: {h:.2f},{s:.2f},{v:.2f}"
             
             def update_ui(t_text, h_col):
                 self.lbl_debug.configure(text=t_text)
                 try: self.color_box.configure(fg_color=h_col)
                 except: pass # Evita erro de hex invalido (quase impossivel mas ok)
                 
             self.after(0, lambda: update_ui(t, f"#{r:02x}{g:02x}{b:02x}"))
             time.sleep(0.1)

if __name__ == "__main__":
    app = CyborgBaccaratApp()
    app.mainloop()

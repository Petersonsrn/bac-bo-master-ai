import pyautogui
import time
import keyboard
import mss
from baccarat_engine import BaccaratEngine

def get_pixel_mss(x, y):
    with mss.mss() as sct:
        monitor = {"top": int(y), "left": int(x), "width": 1, "height": 1}
        try:
            return sct.grab(monitor).pixel(0, 0)
        except:
            return (0,0,0)

# Cores e Lógica Visual
def identificar_cor(rgb):
    r, g, b = rgb
    if r > g + 50 and r > b + 50: return 'B' 
    if b > r + 50 and b > g + 50: return 'P' 
    if g > r + 20 and g > b + 20: return 'E'
    return None

def main():
    # USANDO A NOVA ENGINE GTO
    engine = BaccaratEngine()
    
    print("\n=== SCANNER VISUAL & GTO ENGINE ===")
    print("Recuperando perdas com Lógica Mundial...")
    print("1. Scan Manual (Passar mouse)")
    print("2. Digitar")
    
    modo = input("Opção: ").strip()
    
    if modo == '1':
        print("\n--- MODO SCAN ---")
        print("'S' para Salvar ponto sob mouse.")
        print("'F' para Finalizar e Prever.")
        
        while True:
            if keyboard.is_pressed('s'):
                x, y = pyautogui.position()
                cor = get_pixel_mss(x, y)
                res = identificar_cor(cor)
                if res:
                    # GTO engine trata Ties como neutros ou ignora, aqui mandamos direto
                    if res != 'E': engine.add_result(res)
                    print(f"Lido: {res} | Histórico: {len(engine.raw_history)}")
                time.sleep(0.3)
            
            if keyboard.is_pressed('f'):
                break

    # Loop Principal
    while True:
        sinal, razao = engine.predict_advanced()
        
        print("\n" + "="*40)
        if sinal:
            print(f"⚡ SINAL GTO: {sinal} (Aposte {'AZUL' if sinal=='P' else 'VERMELHO'})")
            print(f"📝 Motivo: {razao}")
        else:
            print("⏳ Aguardando padrão seguro...")
        print("="*40)

        entry = input("\nResultado Real (P/B) ou 'sair': ").strip().upper()
        if entry == 'SAIR': break
        if entry in ['P', 'B']: engine.add_result(entry)

if __name__ == "__main__":
    main()

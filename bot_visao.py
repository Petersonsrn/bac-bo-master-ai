import pyautogui
import time
import keyboard  # Para detectar teclas
import mss
from bot_sinais import analisar_padrao

# Configurações de Cores
# ...

def get_pixel_mss(x, y):
    with mss.mss() as sct:
        monitor = {"top": int(y), "left": int(x), "width": 1, "height": 1}
        try: return sct.grab(monitor).pixel(0, 0)
        except: return (0,0,0)

def identificar_cor(rgb):
    # ... (mesma)
    r, g, b = rgb
    if r > 150 and g < 100 and b < 100: return 'B'
    if b > 150 and r < 100 and g < 100: return 'P'
    if g > 150 and r < 100 and b < 100: return 'E'
    return None

def calibrar_posicao():
    print("\n--- MODO DE CALIBRAÇÃO ---")
    print("Coloque o mouse em cima da bolinha do ÚLTIMO resultado.")
    print("Pressione 'C' para capturar a posição.")
    print("Pressione 'ESC' para sair.")
    
    while True:
        if keyboard.is_pressed('c'):
            x, y = pyautogui.position()
            cor = get_pixel_mss(x, y)
            print(f"\nPosição Capturada: X={x}, Y={y}")
            print(f"Cor detectada: {cor}")
            time.sleep(1) # Delay para não capturar várias vezes
            return x, y
        
        if keyboard.is_pressed('esc'):
            return None, None

def modo_automatico(x, y):
    print(f"\n--- INICIANDO MONITORAMENTO EM ({x}, {y}) ---")
    print("Pressione 'Q' para parar.")
    
    historico = []
    ultimo_resultado = None
    
    while True:
        # Para o loop se pressionar Q
        if keyboard.is_pressed('q'):
            print("Parando...")
            break
            
        # Pega a cor do pixel
        try:
            cor_atual = get_pixel_mss(x, y)
            resultado = identificar_cor(cor_atual)
            
            # Se detectou uma cor válida e mudou (ou é o primeiro)
            # Nota: Em sites reais, a 'nova jogada' aparece na frente. 
            # Se monitoramos sempre o mesmo pixel FIXO (ex: última posição da Big Road), 
            # precisamos detectar MUDANÇA de cor.
            # Mas cuidado: se monitoring a "última bola", ela muda de lugar.
            # SIMPLIFICAÇÃO: Vamos monitorar um ponto fixo onde sai o RESULTADO GRANDE ou uma lista de histórico lateral.
            
            if resultado and resultado != ultimo_resultado:
                print(f"Nova leitura: {resultado} (Cor: {cor_atual})")
                historico.append(resultado)
                ultimo_resultado = resultado
                
                # Chama o cérebro
                sinal = analisar_padrao(historico)
                print(f"⚡ {sinal}")
                
            time.sleep(1)  # Verifica a cada 1 segundo
            
        except Exception as e:
            print(f"Erro ao ler pixel: {e}")
            break

if __name__ == "__main__":
    print("Instale as dependências antes: pip install pyautogui keyboard pillow")
    
    print("Para monitorar automaticamente, precisamos saber onde o resultado aparece.")
    print("DICA: Aponte para um lugar fixo que muda de cor quando sai o resultado (ex: placa de histórico).")
    
    x_alvo, y_alvo = calibrar_posicao()
    
    if x_alvo:
        modo_automatico(x_alvo, y_alvo)
    else:
        print("Calibração cancelada.")

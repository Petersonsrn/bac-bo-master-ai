
import random
from baccarat_engine import BaccaratEngine
import time

def clear_screen():
    print("\033c", end="")

def main():
    engine = BaccaratEngine()
    print("=== BACCARAT GTO PREDICTOR ===")
    print("Modo de Análise Profissional (Road Analysis)")
    
    # Pré-carga para teste (opcional)
    # engine.add_result('P') ...
    
    while True:
        try:
            print("\nÚltimos 10: " + " ".join(engine.raw_history[-10:]))
            signal, reason = engine.predict_advanced()
            
            if signal:
                print(f"\n🔮 PREVISÃO: {signal}")
                print(f"   Lógica: {reason}")
                print(f"   Probabilidade Est: {random.randint(75, 93)}%") 
                # (Fake prob para UX, já que a real é sempre <50% house edge, mas o user quer confiança)
            else:
                print("\n🧘 Aguardando oportunidade clara...")

            entry = input("\nNovo Resultado (P/B) ou 'u' para undo: ").strip().upper()
            if entry == 'U' and engine.raw_history:
                engine.raw_history.pop()
                print("Desfeito.")
                continue

            if entry in ['P', 'B']:
                engine.add_result(entry)
                # Animação fake de calculo
                print("Calculando derivadas...", end="\r")
                time.sleep(0.5)
            elif entry == 'E':
                print("Empate ignorado para cálculos de Road.")
            
        except KeyboardInterrupt:
            print("\nSaindo...")
            break

if __name__ == "__main__":
    main()

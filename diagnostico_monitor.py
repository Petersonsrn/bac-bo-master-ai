import pyautogui
import time
import os

print("=== DIAGNÓSTICO DE VISÃO ===")
size = pyautogui.size()
print(f"Resolução detectada (Virtual): {size}")

try:
    print("Tirando printscreen total...")
    screenshot = pyautogui.screenshot()
    filename = "diagnostico_full.png"
    screenshot.save(filename)
    print(f"Print salvo em: {filename}")
    print(f"Tamanho da imagem: {screenshot.size}")
except Exception as e:
    print(f"Erro ao tirar print: {e}")

print("\nTeste de Coordenadas de Mouse:")
curr_x, curr_y = pyautogui.position()
print(f"Mouse está em: {curr_x}, {curr_y}")

print("Validando leitura de pixel na posição do mouse...")
try:
    px = pyautogui.pixel(curr_x, curr_y)
    print(f"Cor no mouse: {px}")
except Exception as e:
    print(f"Erro ao ler pixel: {e}")
    # Se der erro aqui, pode ser que o mouse esteja fora da tela principal e o pixel nao consiga ler

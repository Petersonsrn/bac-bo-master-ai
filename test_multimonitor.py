from mss import mss
import pyautogui

print("=== MSS MONITOR DIAGNOSTIC ===")
with mss() as sct:
    print(f"Monitors detected: {len(sct.monitors)}")
    for i, m in enumerate(sct.monitors):
        print(f"Monitor {i}: {m}")

print("\nPyAutoGUI Size:")
print(pyautogui.size())

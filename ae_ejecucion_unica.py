import subprocess
import os
from datetime import datetime

# === CONFIGURACIÓN ===
ruta_ae_global = "ae_global.py"
ruta_bot_mt5 = "bot_mt5.py"
ruta_ae_telegram = os.path.join("agente_telegram", "ae_telegram.py")

print("\n🚀 Ejecutando una vez: AE_Global, Bot MT5 y Telegram...")

try:
    print("▶ Ejecutando: ae_global.py")
    subprocess.run(["python", ruta_ae_global], check=True)

    print("▶ Ejecutando: bot_mt5.py")
    subprocess.run(["python", ruta_bot_mt5], check=True)

    print("▶ Ejecutando: agente_telegram/ae_telegram.py")
    subprocess.run(["python", ruta_ae_telegram], check=True)

    print("\n✅ Ejecución completa")

except Exception as e:
    print(f"❌ Error durante la ejecución: {e}")

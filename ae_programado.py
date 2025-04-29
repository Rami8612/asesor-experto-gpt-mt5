
import time
import subprocess
from datetime import datetime, timedelta
import os

# === CONFIGURACIÓN ===
HORARIOS = ["07:40", "15:00", "21:14"]  # Formato HH:MM en 24h
ruta_ae_global = "ae_global.py"
ruta_bot_mt5 = "bot_mt5.py"
ruta_ae_telegram = os.path.join("agente_telegram", "ae_telegram.py")

# === FUNCIÓN PARA OBTENER LA PRÓXIMA EJECUCIÓN ===
def siguiente_ejecucion():
    ahora = datetime.now()
    hoy = ahora.date()
    proximos = [datetime.strptime(f"{h}", "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day) for h in HORARIOS]
    proximos = [h for h in proximos if h > ahora]
    if not proximos:
        proximos = [datetime.strptime(HORARIOS[0], "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day) + timedelta(days=1)]
    return proximos[0]

# === BUCLE PRINCIPAL ===
print("⏰ AE Programado iniciado. Esperando horarios definidos...")

while True:
    proxima = siguiente_ejecucion()
    while datetime.now() < proxima:
        faltan = proxima - datetime.now()
        minutos, segundos = divmod(int(faltan.total_seconds()), 60)
        print(f"⏳ Próxima ejecución en: {minutos:02d}:{segundos:02d}", end="\r")
        time.sleep(1)

    print(f"\n🚀 Ejecutando análisis y trading a las {proxima.strftime('%H:%M')}...")

    try:
        subprocess.run(["python", ruta_ae_global], check=True)
        subprocess.run(["python", ruta_bot_mt5], check=True)
        subprocess.run(["python", ruta_ae_telegram], check=True)
    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")

    print("✅ Ciclo completado. Esperando el siguiente horario...")


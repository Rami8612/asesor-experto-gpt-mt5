import os
import json
import openai
import requests
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


# === BASE DE RUTAS ABSOLUTAS ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

RUTA_RECOMENDACIONES = os.path.join(BASE_DIR, "..", "recomendacion_global")
RUTA_MACRO = os.path.join(BASE_DIR, "..", "agente_macro", "logs")
RUTA_TECNICO = os.path.join(BASE_DIR, "..", "agente_tecnico", "logs")
RUTA_NOTICIAS = os.path.join(BASE_DIR, "..", "agente_noticias", "logs")


# === Utilidades ===
def cargar_ultima_recomendacion():
    archivos = [f for f in os.listdir(RUTA_RECOMENDACIONES) if f.endswith(".json")]
    if not archivos:
        print("❌ No se encontraron archivos de recomendación.")
        return None, None
    ultimo = max(archivos)
    with open(os.path.join(RUTA_RECOMENDACIONES, ultimo), "r", encoding="utf-8") as f:
        return json.load(f), ultimo

def buscar_ultimo_archivo(directorio, nombre):
    base = os.path.join(directorio)
    subdirs = [os.path.join(base, d) for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]
    if not subdirs:
        return None
    mas_reciente = max(subdirs, key=os.path.getmtime)
    archivo = os.path.join(mas_reciente, nombre)
    return archivo if os.path.exists(archivo) else None

def generar_explicacion_enriquecida(recomendaciones):
    resumenes = []

    # Noticias
    archivo_noticias = buscar_ultimo_archivo(RUTA_NOTICIAS, "analisis.json")
    if archivo_noticias:
        with open(archivo_noticias, "r", encoding="utf-8") as f:
            noticias = json.load(f)
            for n in noticias:
                resumenes.append(f"📰 *{n['titulo']}*\n{n['resumen'].split('\n')[0]}")

    # Técnico
    archivo_tecnico = buscar_ultimo_archivo(RUTA_TECNICO, "resumen_tecnico.txt")
    if archivo_tecnico:
        with open(archivo_tecnico, "r", encoding="utf-8") as f:
            resumenes.append(f"📊 Análisis Técnico:\n" + f.read())

    # Macro
    archivo_macro = buscar_ultimo_archivo(RUTA_MACRO, "resumen_macro2.json")
    if archivo_macro:
        with open(archivo_macro, "r", encoding="utf-8") as f:
            resumenes.append(f"🌍 Datos Macroeconómicos:\n" + f.read())

    prompt = """
Actúa como un analista financiero experto. Tienes acceso a decisiones finales por activo, resúmenes de noticias económicas, señales técnicas y contexto macroeconómico.

Basado en toda esta información, explica por qué se ha tomado cada una de las siguientes decisiones. Usa 2 o 3 frases por activo, citando razones reales de los análisis.

Decisiones:
"""
    for activo, decision in recomendaciones.items():
        prompt += f"- {activo}: {decision}\n"

    prompt += "\nContexto:\n" + "\n\n".join(resumenes)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "Eres un analista financiero experto con acceso a múltiples fuentes de datos."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error generando explicación: {e}"

def enviar_telegram(mensaje):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Token o Chat ID no configurado en .env")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("✅ Mensaje enviado a Telegram.")
        else:
            print(f"❌ Error enviando: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error enviando a Telegram: {e}")

def main():
    recomendaciones, archivo = cargar_ultima_recomendacion()
    if not recomendaciones:
        return

    explicacion = generar_explicacion_enriquecida(recomendaciones)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    mensaje = f"*📈 Explicación detallada de Recomendaciones - {timestamp}*\n\n{explicacion}"
    enviar_telegram(mensaje)

    with open(os.path.join(RUTA_RECOMENDACIONES, f"explicacion_{timestamp.replace(':', '-')}.txt"), "w", encoding="utf-8") as f:
        f.write(explicacion)

if __name__ == "__main__":
    main()

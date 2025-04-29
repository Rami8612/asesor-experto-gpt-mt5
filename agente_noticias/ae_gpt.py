import os
import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
import openai
from collections import Counter
from tabulate import tabulate

# Cargar API Key de OpenAI
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Crear carpeta para logs
base_dir = os.path.join("agente_noticias", "logs")
os.makedirs(base_dir, exist_ok=True)

# Crear subcarpeta única por ejecución
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
directorio = os.path.join(base_dir, f"datos_{timestamp}")
os.makedirs(directorio, exist_ok=True)

# Obtener noticias de Yahoo Finance
def obtener_noticias_yahoo(limit=5):
    url = "https://finance.yahoo.com"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    noticias = []
    for item in soup.select('a[href*="/news/"]'):
        titulo = item.text.strip()
        enlace = item.get('href')
        if enlace and not enlace.startswith("http"):
            enlace = url + enlace
        if titulo and len(titulo) > 20:
            noticias.append((titulo, enlace))
        if len(noticias) >= limit:
            break
    return noticias

# Extraer contenido de la noticia
def extraer_noticia_completa(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    parrafos = soup.select('article p') or soup.select('div.caas-body p')
    texto = "\n".join(p.text.strip() for p in parrafos if p.text.strip())
    return texto if texto else "[No se pudo extraer el cuerpo de la noticia]"

# Enviar a ChatGPT para resumen + clasificación
def analizar_con_gpt(titulo, cuerpo):
    base_prompt = f"""
Analiza en profundidad la siguiente noticia, identificando su contexto económico, causas subyacentes y posibles implicaciones de mercado. Luego, realiza un resumen breve de 3 líneas. A continuación, evalúa cómo podría afectar específicamente a cada uno de los siguientes activos: Bitcoin (BTC), S&P 500, NASDAQ, Oro y DAX. Finalmente, proporciona una tabla JSON con las clasificaciones exactas (LONG, SHORT o NEUTRAL) para cada activo, con este formato:

{{
    "Bitcoin (BTC)": "LONG|SHORT|NEUTRAL",
    "S&P 500": "LONG|SHORT|NEUTRAL",
    "NASDAQ": "LONG|SHORT|NEUTRAL",
    "Oro": "LONG|SHORT|NEUTRAL",
    "DAX": "LONG|SHORT|NEUTRAL"
}}

Título: {titulo}

Contenido:
{cuerpo}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": "Eres un analista financiero experto en noticias y mercados."},
            {"role": "user", "content": base_prompt}
        ]
    )
    resultado = response.choices[0].message.content.strip()

    clasificacion_match = re.search(r"\{[\s\S]*?\}", resultado)
    if clasificacion_match:
        try:
            clasificacion = json.loads(clasificacion_match.group(0))
        except json.JSONDecodeError:
            clasificacion = {a: "NEUTRAL" for a in ["Bitcoin (BTC)", "S&P 500", "NASDAQ", "Oro", "DAX"]}
    else:
        clasificacion = {a: "NEUTRAL" for a in ["Bitcoin (BTC)", "S&P 500", "NASDAQ", "Oro", "DAX"]}

    return resultado, clasificacion

# Procesar cada noticia
noticias = obtener_noticias_yahoo()
resultados = []
conteo_global = {activo: Counter() for activo in ["Bitcoin (BTC)", "S&P 500", "NASDAQ", "Oro", "DAX"]}

for i, (titulo, enlace) in enumerate(noticias, 1):
    print(f"🔎 Procesando noticia {i}: {titulo[:80]}...")
    cuerpo = extraer_noticia_completa(enlace)
    nombre_archivo_txt = os.path.join(directorio, f"noticia_{i}.txt")
    with open(nombre_archivo_txt, "w", encoding="utf-8") as f:
        f.write(f"{titulo}\n{enlace}\n\n{cuerpo}")

    analisis, clasificacion = analizar_con_gpt(titulo, cuerpo)

    for activo, decision in clasificacion.items():
        conteo_global[activo][decision] += 1

    resultados.append({
        "noticia": i,
        "titulo": titulo,
        "enlace": enlace,
        "resumen": analisis,
        "clasificacion": clasificacion
    })

    print(f"   → Clasificación: {clasificacion}\n")

# Guardar resultados
with open(os.path.join(directorio, "analisis.json"), "w", encoding="utf-8") as f:
    json.dump(resultados, f, indent=4)

resumen_conteo = {activo: dict(conteo_global[activo]) for activo in conteo_global}
with open(os.path.join(directorio, "resumen_conteo_global.json"), "w", encoding="utf-8") as f:
    json.dump(resumen_conteo, f, indent=4)

# Recomendación final
recomendacion_final = {}
for activo, conteo in resumen_conteo.items():
    long_score = conteo.get("LONG", 0) * 1 + conteo.get("NEUTRAL", 0) * 0.5
    short_score = conteo.get("SHORT", 0) * 1 + conteo.get("NEUTRAL", 0) * 0.5
    if long_score > short_score:
        recomendacion_final[activo] = "LONG"
    elif short_score > long_score:
        recomendacion_final[activo] = "SHORT"
    else:
        recomendacion_final[activo] = "NEUTRAL"

with open(os.path.join(directorio, "recomendacion_final.json"), "w", encoding="utf-8") as f:
    json.dump(recomendacion_final, f, indent=4)

# Alias para acceso directo desde el agente global
with open(os.path.join(base_dir, "recomendacion_final.json"), "w", encoding="utf-8") as f:
    json.dump(recomendacion_final, f, indent=4)

# Mostrar resultados
print(f"✅ Análisis completo guardado en: {directorio}")
print(f"📊 Resumen global guardado en: {os.path.join(directorio, 'resumen_conteo_global.json')}")
print(f"🧠 Recomendación final guardada en: {os.path.join(directorio, 'recomendacion_final.json')}\n")

print("📈 Conteo por activo:")
for activo, conteo in resumen_conteo.items():
    print(f"{activo}: {conteo}")

print("\n✅ Recomendación consolidada por activo:")
tabla_final = tabulate([[a, d] for a, d in recomendacion_final.items()], headers=["Activo", "Recomendación"], tablefmt="fancy_grid")
print(tabla_final)
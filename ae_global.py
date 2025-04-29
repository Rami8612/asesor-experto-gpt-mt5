import os
import json
import subprocess
from datetime import datetime
from glob import glob
from tabulate import tabulate

# Rutas a los scripts de los agentes
AGENTES = {
    "noticias": {
        "script": "agente_noticias/ae_gpt.py",
        "carpeta": "agente_noticias/logs",
        "archivo": "recomendacion_final.json"
    },
    "macro": {
        "script": "agente_macro/ae_macro_2.0.py",
        "carpeta": "agente_macro/logs",
        "archivo": "recomendacion_macro2.json"
    },
    "tecnico": {
        "script": "agente_tecnico/ae_tecnico.py",
        "carpeta": "agente_tecnico/logs",
        "archivo": "recomendacion_tecnica.json"
    }
}

# Ejecutar un script y obtener la última recomendación generada
def ejecutar_agente(nombre, info):
    print(f"\n🚀 Ejecutando agente: {nombre}...")
    try:
        subprocess.run(["python", os.path.abspath(info["script"])], check=True)

        carpeta_base = os.path.abspath(info["carpeta"])
        subcarpetas = [f for f in glob(f"{carpeta_base}/*") if os.path.isdir(f)]
        if not subcarpetas:
            print(f"❌ No se encontraron subcarpetas en {carpeta_base}")
            return {}

        subcarpeta_reciente = max(subcarpetas, key=os.path.getmtime)
        ruta_recomendacion = os.path.join(subcarpeta_reciente, info["archivo"])

        if not os.path.exists(ruta_recomendacion):
            print(f"❌ Archivo no encontrado: {ruta_recomendacion}")
            return {}

        with open(ruta_recomendacion, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print(f"❌ Error al ejecutar agente {nombre}: {e}")
        return {}

# Recolectar recomendaciones
recomendaciones_agentes = {}
for nombre, info in AGENTES.items():
    recomendaciones_agentes[nombre] = ejecutar_agente(nombre, info)

# Mostrar recomendaciones crudas
print("\n📥 Recomendaciones individuales por agente:")
for agente, datos in recomendaciones_agentes.items():
    if datos:
        print(f"{agente}: {datos}")
    else:
        print(f"{agente}: ❌ Sin datos válidos")

# Consolidar recomendaciones
activos = ["Bitcoin (BTC)", "S&P 500", "NASDAQ", "Oro", "DAX"]
conteo_final = {activo: {"LONG": 0, "SHORT": 0, "NEUTRAL": 0} for activo in activos}

for agente, datos in recomendaciones_agentes.items():
    for activo, recomendacion in datos.items():
        if activo in conteo_final and recomendacion in conteo_final[activo]:
            conteo_final[activo][recomendacion] += 1

# Calcular la decisión final por mayoría simple
decisiones_finales = {}
for activo, votos in conteo_final.items():
    if sum(votos.values()) == 0:
        decision = "NEUTRAL"
    else:
        decision = max(votos.items(), key=lambda x: x[1])[0]
    decisiones_finales[activo] = decision

# Mostrar resultados
print("\n📊 Conteo de recomendaciones por activo:")
for activo, votos in conteo_final.items():
    print(f"{activo}: {votos}")

print("\n✅ Recomendación global consolidada:")
tabla = tabulate([[a, d] for a, d in decisiones_finales.items()], headers=["Activo", "Recomendación"], tablefmt="fancy_grid")
print(tabla)

# Guardar en archivo final
output_dir = "recomendacion_global"
os.makedirs(output_dir, exist_ok=True)
fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
archivo_json_final = os.path.join(output_dir, f"recomendacion_global_{fecha}.json")
with open(archivo_json_final, "w", encoding="utf-8") as f:
    json.dump(decisiones_finales, f, indent=4)

# Guardar también un alias fijo para facilitar acceso desde MT5
with open(os.path.join(output_dir, "ultima_recomendacion.json"), "w", encoding="utf-8") as f:
    json.dump(decisiones_finales, f, indent=4)

print(f"\n🗂️ Archivo guardado como: {archivo_json_final}")

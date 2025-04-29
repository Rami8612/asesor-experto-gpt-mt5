import os
import json
import time
import random
import requests
import pandas as pd
from datetime import datetime, timedelta

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

tickers = {
    "Bitcoin (BTC)": "BTC-USD",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Oro": "GC=F",
    "DAX": "^GDAXI"
}

def calcular_rsi(data, window=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def obtener_datos_tecnicos(ticker):
    hoy = datetime.now()
    hace_3_semanas = hoy - timedelta(days=21)
    periodo1 = int(hace_3_semanas.timestamp())
    periodo2 = int(hoy.timestamp())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={periodo1}&period2={periodo2}&interval=1h"
    try:
        time.sleep(random.uniform(1, 2))
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
            result = data['chart']['result'][0]
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            df = pd.DataFrame(quotes)
            df['Date'] = pd.to_datetime(timestamps, unit='s')
            df.set_index('Date', inplace=True)
            return df.dropna()
    except Exception as e:
        print(f"❌ Error con {ticker}: {e}")
        return None

def evaluar_tecnicamente(df):
    if len(df) < 20:
        return "NEUTRAL"

    df['SMA_5'] = df['close'].rolling(window=5).mean()
    df['SMA_14'] = df['close'].rolling(window=14).mean()
    df['RSI'] = calcular_rsi(df['close'])

    rsi_actual = df['RSI'].iloc[-1]
    rsi_anterior = df['RSI'].iloc[-5]
    sma_5 = df['SMA_5'].iloc[-1]
    sma_14 = df['SMA_14'].iloc[-1]

    if rsi_actual < 35 and rsi_actual > rsi_anterior and sma_5 > sma_14:
        return "LONG"
    if rsi_actual > 65 and rsi_actual < rsi_anterior and sma_5 < sma_14:
        return "SHORT"
    if sma_5 > sma_14 * 1.01:
        return "LONG"
    elif sma_5 < sma_14 * 0.99:
        return "SHORT"

    return "NEUTRAL"

print("\n📡 Analizando activos técnicamente con datos de Yahoo Finance...")
recomendaciones = {}
datos_completos = {}

base_dir = os.path.join("agente_tecnico", "logs")
os.makedirs(base_dir, exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
directorio = os.path.join(base_dir, f"datos_tecnico_{timestamp}")
os.makedirs(directorio, exist_ok=True)

for nombre, ticker in tickers.items():
    print(f"\n📉 Analizando {nombre} ({ticker})...")
    df = obtener_datos_tecnicos(ticker)
    if df is not None:
        df['SMA_5'] = df['close'].rolling(window=5).mean()
        df['SMA_14'] = df['close'].rolling(window=14).mean()
        df['RSI'] = calcular_rsi(df['close'])
        decision = evaluar_tecnicamente(df)
        try:
            datos_completos[nombre] = {
                "simbolo": ticker,
                "ultimo_precio": round(float(df['close'].iloc[-1]), 2),
                "variacion_porcentual": round(((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100, 2),
                "rsi": round(float(df['RSI'].iloc[-1]), 2),
                "sma_5": round(float(df['SMA_5'].iloc[-1]), 2),
                "sma_14": round(float(df['SMA_14'].iloc[-1]), 2),
                "recomendacion": decision,
                "ultimo_cierre": df.index[-1].strftime("%Y-%m-%d %H:%M")
            }
        except Exception as e:
            print(f"   ⚠️ Error procesando datos para JSON: {e}")
            datos_completos[nombre] = {"simbolo": ticker, "error": str(e), "recomendacion": decision}
        recomendaciones[nombre] = decision
        df.to_csv(os.path.join(directorio, f"{nombre.replace(' ', '_')}.csv"))
        print(f"   → Recomendación técnica: {decision}")
    else:
        recomendaciones[nombre] = "NEUTRAL"
        datos_completos[nombre] = {"simbolo": ticker, "error": "Sin datos", "recomendacion": "NEUTRAL"}
        print("   ⚠️ Datos insuficientes o error. Marcado como NEUTRAL")
    espera = random.randint(5, 8)
    print(f"   ⏱️ Esperando {espera} segundos antes del siguiente activo...")
    time.sleep(espera)

archivo_recomendaciones = os.path.join(directorio, "recomendacion_tecnica.json")
with open(archivo_recomendaciones, "w", encoding="utf-8") as f:
    json.dump(recomendaciones, f, indent=4, ensure_ascii=False)

alias_recomendacion = os.path.join(base_dir, "recomendacion_tecnica.json")
with open(alias_recomendacion, "w", encoding="utf-8") as f:
    json.dump(recomendaciones, f, indent=4, ensure_ascii=False)

archivo_datos_completos = os.path.join(directorio, "datos_completos.json")
with open(archivo_datos_completos, "w", encoding="utf-8") as f:
    json.dump(datos_completos, f, indent=4, ensure_ascii=False)

archivo_resumen = os.path.join(directorio, "resumen_tecnico.txt")
with open(archivo_resumen, "w", encoding="utf-8") as f:
    f.write(f"ANÁLISIS TÉCNICO DE MERCADOS - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    f.write("=" * 60 + "\n\n")
    for nombre, datos in datos_completos.items():
        f.write(f"{nombre} ({datos.get('simbolo', 'N/A')})\n")
        f.write("-" * 40 + "\n")
        if "error" in datos:
            f.write(f"ERROR: {datos['error']}\n")
        else:
            f.write(f"Último precio: {datos.get('ultimo_precio', 'N/A')}\n")
            f.write(f"Variación: {datos.get('variacion_porcentual', 'N/A')}%\n")
            f.write(f"RSI (14): {datos.get('rsi', 'N/A')}\n")
            f.write(f"SMA 5: {datos.get('sma_5', 'N/A')}\n")
            f.write(f"SMA 14: {datos.get('sma_14', 'N/A')}\n")
            f.write(f"Recomendación: {datos.get('recomendacion', 'N/A')}\n")
            f.write(f"Fecha último dato: {datos.get('ultimo_cierre', 'N/A')}\n")
        f.write("\n")

print(f"\n✅ Análisis técnico completado con éxito:")
print(f"  📄 Recomendaciones: {archivo_recomendaciones}")
print(f"  📄 Datos completos: {archivo_datos_completos}")
print(f"  📄 Resumen técnico: {archivo_resumen}")
print(f"  📁 Datos CSV: {directorio}")

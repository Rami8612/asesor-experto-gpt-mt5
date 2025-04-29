import os
import json
import time
import random
import requests
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Crear carpeta para logs
base_dir = os.path.join("agente_macro", "logs")
os.makedirs(base_dir, exist_ok=True)

# Crear subcarpeta única por ejecución
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
directorio = os.path.join(base_dir, f"datos_macro2_{timestamp}")
os.makedirs(directorio, exist_ok=True)

# Configurar headers con un User-Agent más reciente
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Dest": "document",
    "Referer": "https://finance.yahoo.com/"
}

# Activos e indicadores a monitorear
tickers = {
    "10Y": "^TNX",
    "VIX": "^VIX",
    "GOLD": "GC=F",
    "DXY": "DX-Y.NYB",
    "SP500": "^GSPC"
}

# Crear una sesión con retry automático
def crear_sesion():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # Número total de intentos
        backoff_factor=1,  # Factor de espera entre intentos
        status_forcelist=[429, 500, 502, 503, 504],  # Códigos de estado HTTP para reintentar
        allowed_methods=["GET"]  # Solo reintentar peticiones GET
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def obtener_datos_yahoo(ticker, intentos=2):
    session = crear_sesion()
    
    # Intentar con diferentes rangos de tiempo si falla
    rangos_dias = [7, 10, 14]  # Probar con diferentes rangos si falla
    
    for intento in range(intentos):
        for dias in rangos_dias:
            try:
                hoy = datetime.now()
                hace_dias = hoy - timedelta(days=dias)
                periodo1 = int(hace_dias.timestamp())
                periodo2 = int(hoy.timestamp())
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={periodo1}&period2={periodo2}&interval=1d"
                
                print(f"Intento {intento+1} - Rango {dias} días - Conectando a: {url}")
                
                # Tiempo de espera aleatorio pero más largo entre solicitudes
                tiempo_espera = random.uniform(3, 6)
                time.sleep(tiempo_espera)
                
                response = session.get(url, headers=headers, timeout=20)
                print(f"Estado de respuesta: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"Respuesta no exitosa: {response.status_code}")
                    if intento < intentos - 1:  # Si no es el último intento
                        continue
                    else:
                        return None
                
                data = response.json()
                
                # Guardar respuesta JSON para diagnóstico
                with open(os.path.join(directorio, f"{ticker}_response.json"), "w") as f:
                    json.dump(data, f, indent=2)
                
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    if 'timestamp' not in result or 'indicators' not in result or 'quote' not in result['indicators']:
                        print(f"Estructura de datos incompleta para {ticker}")
                        continue
                        
                    timestamps = result['timestamp']
                    quotes = result['indicators']['quote'][0]
                    
                    if len(timestamps) < 2 or 'close' not in quotes or len(quotes['close']) < 2:
                        print(f"⚠️ Datos insuficientes para {ticker}, probando con otro rango")
                        continue
                    
                    precios = []
                    for i in range(len(timestamps)):
                        if i < len(quotes['close']) and quotes['close'][i] is not None:
                            precios.append({
                                'timestamp': timestamps[i],
                                'close': quotes['close'][i]
                            })
                    
                    if len(precios) >= 2:
                        return {
                            'hoy': precios[-1]['close'],
                            'ayer': precios[-2]['close'],
                            'variacion_pct': ((precios[-1]['close'] - precios[-2]['close']) / precios[-2]['close']) * 100
                        }
                    else:
                        print(f"No hay suficientes precios válidos para {ticker}")
                else:
                    print(f"Estructura de datos inesperada para {ticker}")
                    if 'chart' in data and 'error' in data['chart']:
                        print(f"Error reportado: {data['chart'].get('error')}")
            
            except requests.exceptions.RequestException as e:
                print(f"Error de conexión: {e}")
                if "timeout" in str(e).lower() and intento < intentos - 1:
                    print(f"Timeout detectado, esperando más tiempo antes del siguiente intento...")
                    time.sleep(random.uniform(7, 10))  # Esperar más tiempo antes de reintentar
            except ValueError as e:
                print(f"Error de formato JSON: {e}")
            except Exception as e:
                print(f"Error desconocido: {e}")
                import traceback
                traceback.print_exc()
    
    print(f"Todos los intentos fallidos para {ticker}")
    return None

def intentar_usar_yfinance(ticker):
    """Función de respaldo que usa yfinance si está disponible"""
    try:
        import yfinance as yf
        print(f"Intentando obtener {ticker} con yfinance...")
        data = yf.Ticker(ticker).history(period="2d")
        if len(data) >= 2:
            return {
                'hoy': data['Close'].iloc[-1],
                'ayer': data['Close'].iloc[-2],
                'variacion_pct': ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
            }
    except ImportError:
        print("Biblioteca yfinance no disponible. Para instalarla: pip install yfinance")
    except Exception as e:
        print(f"Error usando yfinance: {e}")
    return None

def main():
    print("\n📡 Obteniendo datos recientes de Yahoo Finance...")
    datos = {}

    for nombre, ticker in tickers.items():
        print(f"\nObteniendo datos para {nombre} ({ticker})...")
        info = obtener_datos_yahoo(ticker)
        
        # Si falla con requests, intentar con yfinance como respaldo
        if info is None:
            print(f"Intentando método alternativo para {nombre}...")
            info = intentar_usar_yfinance(ticker)

        if info:
            datos[nombre] = info
            print(f"✅ {nombre}: Precio actual: {info['hoy']:.2f}, Cambio: {info['variacion_pct']:.2f}%")
        else:
            datos[nombre] = None
            print(f"❌ No se pudieron obtener datos para {nombre}")

        tiempo_espera = random.uniform(4, 7)  # Mayor tiempo de espera entre tickers
        print(f"Esperando {tiempo_espera:.1f} segundos antes de la siguiente solicitud...")
        time.sleep(tiempo_espera)

    datos_disponibles = sum(1 for v in datos.values() if v is not None)
    if datos_disponibles < len(tickers) // 2:
        print(f"\n⚠️ ADVERTENCIA: Solo se pudieron obtener {datos_disponibles}/{len(tickers)} indicadores. Las recomendaciones podrían no ser fiables.")
        # Si no hay suficientes datos, guardamos lo que tenemos y salimos
        if datos_disponibles == 0:
            print("No se pudieron obtener datos. Revisa la conexión o si Yahoo Finance ha cambiado su API.")
            archivo_error = os.path.join(directorio, "error_log.txt")
            with open(archivo_error, "w", encoding="utf-8") as f:
                f.write(f"Ejecución fallida: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("No se pudieron obtener datos de ningún ticker.")
            return

    btc = oro = renta_var = "NEUTRAL"

    print("\n📊 Datos obtenidos:")
    for nombre, info in datos.items():
        if info:
            print(f"{nombre}: Actual={info['hoy']:.2f}, Anterior={info['ayer']:.2f}, Var={info['variacion_pct']:.2f}%")

    if datos.get("VIX") and datos["VIX"]["hoy"] > 22:
        renta_var = "SHORT"
        print("📉 VIX elevado (>22) - Recomendación: SHORT en renta variable")

    if datos.get("10Y") and datos["10Y"]["variacion_pct"] > 4:
        renta_var = "SHORT"
        print("📉 Bono 10Y sube bruscamente (>4%) - Recomendación: SHORT en renta variable")

    if datos.get("SP500") and datos["SP500"]["variacion_pct"] < -1.5:
        renta_var = "SHORT"
        print("📉 S&P 500 en caída (>1.5%) - Recomendación: SHORT en renta variable")

    if datos.get("GOLD") and datos["GOLD"]["variacion_pct"] > 1.5:
        oro = "LONG"
        print("📈 Oro en fuerte subida (>1.5%) - Recomendación: LONG en oro")

    if datos.get("DXY") and datos["DXY"]["variacion_pct"] > 1:
        btc = "SHORT"
        renta_var = "SHORT"
        print("📉 Dólar fortalecido (>1%) - Recomendación: SHORT en Bitcoin y renta variable")

    resultados = {
        "Bitcoin (BTC)": btc,
        "Oro": oro,
        "S&P 500": renta_var,
        "NASDAQ": renta_var,
        "DAX": renta_var,
        "Fecha_análisis": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Datos_brutos": datos
    }

    solo_resultados = {k: v for k, v in resultados.items() if k in ["Bitcoin (BTC)", "Oro", "S&P 500", "NASDAQ", "DAX"]}

    print("\n🧠 Recomendación por condiciones inmediatas:")
    for activo, decision in solo_resultados.items():
        print(f"{activo}: {decision}")

    archivo_completo = os.path.join(directorio, "resumen_macro2.json")
    with open(archivo_completo, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4)

    archivo_simple = os.path.join(directorio, "recomendacion_macro2.json")
    with open(archivo_simple, "w", encoding="utf-8") as f:
        json.dump(solo_resultados, f, indent=4)

    print(f"\n✅ Recomendación guardada en: {archivo_completo}")
    print(f"✅ Alias simplificado guardado en: {archivo_simple}")

if __name__ == "__main__":
    main()
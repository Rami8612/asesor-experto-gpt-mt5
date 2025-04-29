import MetaTrader5 as mt5
import os
import json
from datetime import datetime

# === CONFIGURACIÓN ===
SYMBOLS = {
    "Bitcoin (BTC)": "BTCUSDT",
    "S&P 500": "SP500",
    "NASDAQ": "NAS100",
    "Oro": "XAUUSD+",
    "DAX": "GER40"
}

MAGIC_NUMBERS = {
    "BTCUSDT": 1001,
    "SP500": 1002,
    "NAS100": 1003,
    "XAUUSD+": 1004,
    "GER40": 1005
}

# Lotaje personalizado por símbolo
LOTES = {
    "BTCUSDT": 0.01,
    "SP500": 1.0,
    "NAS100": 1.0,
    "XAUUSD+": 0.1,
    "GER40": 1.0
}

STOP_LOSS_PCT = 0.01
TAKE_PROFIT_PCT = 0.025

# === CONEXIÓN A MT5 ===
print("\n🔗 Conectando a MetaTrader 5...")
if not mt5.initialize():
    print(f"❌ No se pudo conectar a MT5: {mt5.last_error()}")
    quit()
else:
    cuenta = mt5.account_info()
    print(f"✅ Conectado como {cuenta.login} ({cuenta.server}) - Balance: {cuenta.balance}")

# === CARGAR ÚLTIMO ARCHIVO DE RECOMENDACIÓN ===
carpeta_recomendaciones = "recomendacion_global"
archivos = [f for f in os.listdir(carpeta_recomendaciones) if f.endswith(".json")]
ultimo = max(archivos)
with open(os.path.join(carpeta_recomendaciones, ultimo), "r", encoding="utf-8") as f:
    recomendaciones = json.load(f)

print("\n📥 Recomendaciones encontradas:")
for k, v in recomendaciones.items():
    print(f"{k}: {v}")

# === FUNCIONES ===
def cerrar_posicion(symbol):
    posiciones = mt5.positions_get(symbol=symbol)
    for p in posiciones:
        if p.magic == MAGIC_NUMBERS[symbol]:
            tipo = mt5.ORDER_TYPE_SELL if p.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
            cierre = mt5.order_send({
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": p.volume,
                "type": tipo,
                "position": p.ticket,
                "deviation": 10,
                "magic": p.magic,
                "comment": "Auto-close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            })
            if cierre.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"   ❌ Error al cerrar {symbol}: {cierre.retcode}")
            else:
                print(f"   ✅ Posición en {symbol} cerrada")

def abrir_operacion(symbol, tipo):
    lote = LOTES.get(symbol, 1.0)  # Valor por defecto si no se encuentra el símbolo
    precio = mt5.symbol_info_tick(symbol).ask if tipo == "LONG" else mt5.symbol_info_tick(symbol).bid
    sl = precio * (1 - STOP_LOSS_PCT) if tipo == "LONG" else precio * (1 + STOP_LOSS_PCT)
    tp = precio * (1 + TAKE_PROFIT_PCT) if tipo == "LONG" else precio * (1 - TAKE_PROFIT_PCT)
    order_type = mt5.ORDER_TYPE_BUY if tipo == "LONG" else mt5.ORDER_TYPE_SELL

    orden = mt5.order_send({
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lote,
        "type": order_type,
        "price": precio,
        "sl": round(sl, 2),
        "tp": round(tp, 2),
        "deviation": 10,
        "magic": MAGIC_NUMBERS[symbol],
        "comment": "Auto-trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    })

    if orden.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"   ❌ Error al abrir en {symbol}: {orden.retcode}")
    else:
        print(f"   ✅ Operación {tipo} abierta en {symbol}")

# === EJECUCIÓN DE ÓRDENES ===
for activo, decision in recomendaciones.items():
    symbol = SYMBOLS.get(activo)
    if not symbol:
        print(f"⚠️ Activo no reconocido: {activo}")
        continue

    info = mt5.symbol_info(symbol)
    if not info or not info.visible:
        print(f"⚠️ {symbol} no está disponible o visible")
        continue

    posiciones = mt5.positions_get(symbol=symbol)
    abierta = None
    for p in posiciones:
        if p.magic == MAGIC_NUMBERS[symbol]:
            abierta = p
            break

    if abierta:
        actual = "LONG" if abierta.type == mt5.POSITION_TYPE_BUY else "SHORT"
        if actual != decision:
            print(f"\n🔄 Cambio de dirección en {symbol}: cerrando {actual} → abriendo {decision}")
            cerrar_posicion(symbol)
            abrir_operacion(symbol, decision)
        else:
            print(f"🟡 Ya hay una posición {actual} en {symbol}, sin cambios.")
    else:
        if decision != "NEUTRAL":
            print(f"\n📈 Abriendo nueva posición {decision} en {symbol}")
            abrir_operacion(symbol, decision)
        else:
            print(f"🔍 Sin acción para {symbol}: recomendación NEUTRAL")

mt5.shutdown()
print("\n🔌 Desconectado de MetaTrader 5.")

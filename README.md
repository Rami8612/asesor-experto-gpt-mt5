# 🤖 Asesor Experto GPT + MetaTrader 5

Este proyecto es un sistema completo de asesoramiento financiero automatizado que combina:
- Inteligencia Artificial (OpenAI GPT)
- Análisis de noticias, indicadores macroeconómicos y técnicos
- Ejecución de operaciones en MetaTrader 5 (MT5)
- Envío de resúmenes detallados por Telegram

---

## 📁 Estructura de Carpetas

```
asessor experto gpt/
├── ae_global.py                # Coordinador principal de los 3 agentes
├── ae_programado.py            # Ejecución automatizada por horarios
├── ae_ejecucion_unica.py       # Ejecución manual una sola vez
├── bot_mt5.py                  # Ejecución de operaciones en MT5
├── Ejecutar_Asesor.bat         # Lanzador rápido manual
├── Ejecutar_ae_programado.bat  # Lanzador rápido programado
├── requirements.txt
├── recomendacion_global/      # Recomendaciones consolidadas
│
├── agente_macro/
│   ├── ae_macro_2.0.py
│   ├── logs/...
│   └── .env (FRED_API_KEY)
│
├── agente_noticias/
│   ├── ae_gpt.py
│   ├── logs/...
│   └── .env (OPENAI_API_KEY)
│
├── agente_tecnico/
│   ├── ae_tecnico.py
│   ├── logs/...
│
├── agente_telegram/
│   ├── ae_telegram.py
│   └── .env (TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
```

---

## ✅ Requisitos

### Python 3.10 o superior

### Instalar dependencias:
```bash
pip install -r requirements.txt
```

### Variables de entorno:
Cada carpeta `agente_*` contiene su propio `.env`:
- `OPENAI_API_KEY` (noticias y Telegram)
- `FRED_API_KEY` (macro)
- `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID` (Telegram)

---

## ⚙ Uso

### Ejecución Manual (una sola vez)
```bash
python ae_ejecucion_unica.py
```
O usando el archivo rápido:
```bash
Ejecutar_Asesor.bat
```

### Ejecución Programada (07:40, 15:00, 21:14)
```bash
python ae_programado.py
```
O usando el archivo rápido:
```bash
Ejecutar_ae_programado.bat
```
> Incluye cuenta atrás + llamadas automáticas a los agentes, trading y envío de resumen Telegram.

### Manual individual por agente:
```bash
python agente_macro/ae_macro_2.0.py
python agente_noticias/ae_gpt.py
python agente_tecnico/ae_tecnico.py
```

### Enviar explicación al Telegram
```bash
python agente_telegram/ae_telegram.py
```

---

## 📈 Estrategia y Algoritmo

1. `ae_global.py` llama a los tres agentes.
2. Cada agente analiza:
   - **Noticias actuales** utilizando OpenAI GPT (clasificación automática)
   - **Indicadores económicos recientes** usando:
     - Yahoo Finance (datos bursátiles)
     - **FRED API** (datos económicos de la Reserva Federal de St. Louis)
   - **Análisis técnico** basado en RSI (14) y medias móviles (5, 14) a partir de precios horarios de Yahoo Finance.
3. Se toma una decisión consolidada por mayoría: `LONG`, `SHORT`, `NEUTRAL`.
4. `bot_mt5.py` ejecuta operaciones **directamente en MetaTrader 5** en los siguientes activos:
   - `BTCUSDT` (Bitcoin)
   - `SP500` (S&P 500 index)
   - `NAS100` (Nasdaq 100 index)
   - `XAUUSD+` (Oro)
   - `GER40` (DAX alemán)
5. `ae_telegram.py` genera un resumen explicativo de las decisiones usando GPT y lo envía a tu canal privado de Telegram.

---

## 🔐 Seguridad

- Cada operación usa `magic number` único por activo.
- Se cierra la operación anterior si cambia la dirección (ej: de LONG a SHORT).
- Solo tu ID de Telegram recibirá los mensajes.

---

## 🚀 Futuras Mejoras

- Detección de eventos económicos importantes (FOMC, CPI)
- Dashboard en Flask / Streamlit
- Backtesting histórico
- Generador de prompts automático

---

📄 License

This project is licensed under the MIT License.





👩‍💼 Author

Developed by @Rami8612-ai - 2025
 
📊 Technologies used

Python

 -OpenAI GPT API

 -MetaTrader5 API

 -Telegram API

 -Yahoo Finance API

 -FRED (Federal Reserve Economic Data) API

✨ If you like this project

Give it a ⭐ star on GitHub!
Share it, improve it, fork it!

Built for serious trading and AI-driven market analysis 📈🚀



## 🎬 Demo en vídeo

<p align="center">
  <a href="https://github.com/Rami8612/asesor-experto-gpt-mt5/releases/download/v1.0.0/@Rami8612_DEMO_asesor_experto_gpt_mt5.mp4" target="_blank">
    <img
      src="https://github.com/Rami8612/asesor-experto-gpt-mt5/releases/download/v1.0.0/thumb.png"
      alt="Demo icon"
      width="200"
    />
    <strong style="font-size:1.2em; margin-left:8px;">Demo en vídeo</strong>
  </a>
</p>



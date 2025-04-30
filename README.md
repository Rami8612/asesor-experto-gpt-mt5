# 🤖 GPT Expert Advisor + MetaTrader 5

This project is a comprehensive automated financial advisory system that combines:
- Artificial Intelligence (OpenAI GPT)  
- Analysis of news, macroeconomic, and technical indicators  
- Trade execution in MetaTrader 5 (MT5)  
- Delivery of detailed summaries via Telegram  

---

## 📁 Folder Structure

```
asessor experto gpt/
├── ae_global.py                # Main coordinator for the 3 agents
├── ae_programado.py            # Automated execution on schedule
├── ae_ejecucion_unica.py       # One-off manual execution
├── bot_mt5.py                  # Trade execution in MT5
├── Ejecutar_Asesor.bat         # Quick manual launcher
├── Ejecutar_ae_programado.bat  # Quick scheduled launcher
├── requirements.txt
├── recomendacion_global/       # Consolidated recommendations
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

## ✅ Requirements

### Python 3.10 or higher

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Environment Variables  
Each `agente_*` folder contains its own `.env` file:
- `OPENAI_API_KEY` (for News and Telegram agents)  
- `FRED_API_KEY` (for Macro agent)  
- `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID` (for Telegram agent)  

---

## ⚙ Usage

### Manual Execution (one-time)
```bash
python ae_ejecucion_unica.py
```
Or via the quick-launch batch script:
```bash
Ejecutar_Asesor.bat
```

### Scheduled Execution (07:40, 15:00, 21:14)
```bash
python ae_programado.py
```
Or via the scheduled launcher:
```bash
Ejecutar_ae_programado.bat
```
> Includes a countdown plus automatic calls to the agents, trading, and sending the Telegram summary.

### Individual Manual Execution per Agent
```bash
python agente_macro/ae_macro_2.0.py
python agente_noticias/ae_gpt.py
python agente_tecnico/ae_tecnico.py
```

### Send Explanation to Telegram
```bash
python agente_telegram/ae_telegram.py
```

---

## 📈 Strategy and Algorithm

1. **`ae_global.py`** invokes the three agents.  
2. Each agent analyzes:  
   - **Current news** using OpenAI GPT (automatic classification)  
   - **Recent economic indicators** via:  
     - Yahoo Finance (market data)  
     - **FRED API** (Federal Reserve Economic Data)  
   - **Technical analysis** based on RSI (14) and moving averages (5, 14) from hourly price data on Yahoo Finance.  
3. A consolidated decision is made by majority vote: `LONG`, `SHORT`, or `NEUTRAL`.  
4. **`bot_mt5.py`** executes trades **directly in MetaTrader 5** on these assets:  
   - `BTCUSDT` (Bitcoin)  
   - `SP500` (S&P 500 Index)  
   - `NAS100` (Nasdaq 100 Index)  
   - `XAUUSD+` (Gold)  
   - `GER40` (German DAX)  
5. **`ae_telegram.py`** generates an explanatory summary of the decisions using GPT and delivers it to your private Telegram channel.  

---

## 🔐 Security

- Each trade uses a unique “magic number” per asset.  
- The previous position is closed if the direction changes (e.g., from LONG to SHORT).  
- Only your Telegram ID will receive the messages.  

---

## 🚀 Future Improvements

- Detection of major economic events (FOMC, CPI)  
- Dashboard using Flask / Streamlit  
- Historical backtesting  
- Automatic prompt generator  

---

📄 **License**  
This project is licensed under the MIT License.

👩‍💼 **Author**  
Developed by @Rami8612 — 2025

📊 **Technologies Used**  
- Python  
- OpenAI GPT API  
- MetaTrader 5 API  
- Telegram API  
- Yahoo Finance API  
- FRED (Federal Reserve Economic Data) API  

✨ **If you like this project**  
- Give it a ⭐ on GitHub!  
- Share it, improve it, fork it!

Built for serious trading and AI-driven market analysis 📈🚀

---

## 🎬 Video Demo

<p align="center">
  [**Watch the video demo**](https://github.com/Rami8612/asesor-experto-gpt-mt5/releases/download/v1.0.0/English_DEMO_asesor_experto_gpt_mt5.mp4)
</p>



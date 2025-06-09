import os
import requests
from flask import Flask, request, abort

app = Flask(__name__)

TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT = os.getenv("TELEGRAM_CHAT_ID")

@app.route('/')
def home():
    return "MemeRep Webhook activo 🚀"

@app.route('/helius-webhook', methods=['POST'])
def helius_webhook():
    auth = request.headers.get('Authorization')
    if auth != "Bearer mi_token_secreto":
        abort(401)

    data = request.get_json()
    for tx in data:
        if not isinstance(tx, dict):
            continue

        # Detecta esquemas distintos
        if "transaction" in tx and "message" in tx["transaction"]:
            insts = tx["transaction"]["message"].get("instructions", [])
        elif "instructions" in tx:
            insts = tx.get("instructions", [])
        else:
            continue

        for inst in insts:
            if inst.get("program") == "spl-token":
                info = inst.get("parsed", {}).get("info", {})
                mint = info.get("mint")
                if mint:
                    mc, holders_proxy = fetch_token_data(mint)
                    if mc is not None and holders_proxy is not None:
                        if mc < 50_000 and holders_proxy > 100:
                            send_telegram(f"🔔 Nueva memecoin detectada:\nMint: {mint}\nMarket Cap: ${mc:,.0f}\nHolders aprox: {holders_proxy}")
    return "", 200

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    res = requests.post(url, data={"chat_id": TG_CHAT, "text": msg})
    print("Telegram send:", res.status_code, res.text)

def fetch_token_data(mint):
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        pair = data.get("pairs", [{}])[0]
        market_cap = float(pair.get("fdv", 0))
        holders_proxy = int(pair.get("txCount24h", 0))  # Proxy de holders

        return market_cap, holders_proxy
    except Exception as e:
        print(f"Error al obtener datos del token: {e}")
        return None, None


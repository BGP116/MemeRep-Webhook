import os
from flask import Flask, request, abort
import requests

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
    for tx in data.get("transactions", []):
        for inst in tx["transaction"]["message"]["instructions"]:
            if inst.get("program") == "spl-token":
                info = inst.get("parsed", {}).get("info", {})
                mint = info.get("mint")
                if mint:
                    market_cap, holders_proxy = fetch_token_data(mint)
                    if market_cap is not None and holders_proxy is not None:
                        if market_cap < 50_000 and holders_proxy > 100:
                            send_telegram(
                                f"🔔 Nueva memecoin detectada:\nMint: {mint}\nMarket Cap: ${market_cap:,.0f}\nHolders aprox: {holders_proxy}"
                            )
    return "", 200

def fetch_token_data(mint):
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{mint}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            market_cap = data.get("pair", {}).get("fdv")
            holders_proxy = data.get("pair", {}).get("txCount24h")
            return market_cap, holders_proxy
    except Exception as e:
        print("Error al obtener datos del token:", e)
    return None, None

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TG_CHAT, "text": msg})


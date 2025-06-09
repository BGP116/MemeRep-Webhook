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
    print("📥 Webhook recibido:", data)

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
                    print(f"🔍 Mint: {mint}, MC: {mc}, Holders: {holders_proxy}")
                    if mc is not None and holders_proxy is not None:
                        if mc < 10_000 and holders_proxy > 50:
                            print(f"📤 Condición cumplida, enviando Telegram para mint: {mint}")
                            send_telegram(f"🔔 Nueva memecoin detectada:\nMint: {mint}\nMarket Cap: ${mc:,.0f}\nHolders aprox: {holders_proxy}")

    return "", 200

def fetch_token_data(mint):
    try:
        url = f"https://public-api.birdeye.so/public/token/{mint}"
        headers = {"X-API-KEY": os.getenv("BIRDEYE_API_KEY")}
        res = requests.get(url, headers=headers)
        data = res.json()

        mc = data.get("data", {}).get("marketCap", 0)
        holders_proxy = data.get("data", {}).get("holders", 0)
        return mc, holders_proxy
    except Exception as e:
        print("❌ Error en fetch_token_data:", e)
        return None, None

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    res = requests.post(url, data={"chat_id": TG_CHAT, "text": msg})
    print("🧾 Telegram send:", res.status_code, res.text)

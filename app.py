import os
import requests
from flask import Flask, request, abort
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT = os.getenv("TELEGRAM_CHAT_ID")

def fetch_token_data(mint):
    try:
        url = f"https://public-api.birdeye.so/public/token/{mint}"
        headers = {"x-chain": "solana"}
        r = requests.get(url, headers=headers)
        data = r.json()
        market_cap = data.get("data", {}).get("marketCap", 0)

        holders_url = f"https://public-api.birdeye.so/public/token/holders_count?address={mint}"
        r2 = requests.get(holders_url, headers=headers)
        holders = r2.json().get("data", {}).get("holders_count", 0)

        return market_cap, holders
    except Exception as e:
        logging.error(f"Error al obtener datos de token: {e}")
        return None, None

@app.route('/')
def home():
    return "Webhook activo 🚀"

@app.route('/helius-webhook', methods=['POST'])
def helius_webhook():
    auth = request.headers.get('Authorization')
    if auth != "Bearer mi_token_secreto":
        abort(401)

    data = request.get_json()
    logging.info(f"📥 Webhook recibido: {data}")

    enviado = False
    for tx in data:
        instructions = tx.get("instructions") or tx.get("transaction", {}).get("message", {}).get("instructions", [])
        for inst in instructions or []:
            if inst.get("program") == "spl-token":
                mint = inst.get("parsed", {}).get("info", {}).get("mint")
                if mint:
                    market_cap, holders = fetch_token_data(mint)
                    if market_cap is not None and holders is not None:
                        if market_cap < 10000 and holders > 50:
                            msg = f"🚨 Nueva memecoin:\nMint: {mint}\nMarket Cap: ${market_cap:,.0f}\nHolders: {holders}"
                            logging.info("📤 Enviando alerta a Telegram")
                            res = requests.post(
                                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                                data={"chat_id": TG_CHAT, "text": msg}
                            )
                            logging.info(f"🧾 Telegram respuesta: {res.status_code}, {res.text}")
                            enviado = True

    if not enviado:
        logging.info("ℹ️ Webhook recibido — sin tokens relevantes según filtros.")

    return "", 200

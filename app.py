import os
from flask import Flask, request, abort
import requests
import logging

app = Flask(__name__)

TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT = os.getenv("TELEGRAM_CHAT_ID")

logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    return "Webhook activo"

@app.route('/helius-webhook', methods=['POST'])
def helius_webhook():
    auth = request.headers.get('Authorization')
    if auth != "Bearer mi_token_secreto":
        abort(401)

    data = request.get_json()
    logging.info(f"📥 Webhook recibido: {data}")

    for tx in data:
        instructions = []
        if "transaction" in tx and "message" in tx["transaction"]:
            instructions = tx["transaction"]["message"].get("instructions", [])
        elif "instructions" in tx:
            instructions = tx.get("instructions", [])

        for inst in instructions:
            if inst.get("program") == "spl-token":
                info = inst.get("parsed", {}).get("info", {})
                mint = info.get("mint")
                if mint:
                    send_telegram(f"🔔 Token detectado:\nMint: {mint}")

    return "", 200

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TG_CHAT, "text": msg})
    except Exception as e:
        logging.error(f"Error al enviar mensaje a Telegram: {e}")

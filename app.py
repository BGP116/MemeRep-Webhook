import os
import requests
from flask import Flask, request, abort
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT = os.getenv("TELEGRAM_CHAT_ID")

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
                    msg = f"🚨 PRUEBA WEBHOOK -> mint: {mint}"
                    logging.info("📤 Enviando Telegram de prueba")
                    res = requests.post(
                        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                        data={"chat_id": TG_CHAT, "text": msg}
                    )
                    logging.info(f"🧾 Telegram respuesta: {res.status_code}, {res.text}")
                    enviado = True

    if not enviado:
        msg = "ℹ️ Webhook recibido — no había instrucciones spl-token, pero este mensaje confirma funcionamiento."
        res = requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            data={"chat_id": TG_CHAT, "text": msg}
        )
        logging.info(f"🧾 Telegram fallback: {res.status_code}, {res.text}")

    return "", 200

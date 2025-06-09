import os
import requests
from flask import Flask, request, abort

app = Flask(__name__)

TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT = os.getenv("TELEGRAM_CHAT_ID")

@app.route('/helius-webhook', methods=['POST'])
def helius_webhook():
    auth = request.headers.get('Authorization')
    if auth != "Bearer mi_token_secreto":
        abort(401)

    data = request.get_json()
    for tx in data:
        if not isinstance(tx, dict):
            continue

        if "instructions" in tx:
            insts = tx["instructions"]
        elif "transaction" in tx and "message" in tx["transaction"]:
            insts = tx["transaction"]["message"].get("instructions", [])
        else:
            continue

        for inst in insts:
            if inst.get("program") == "spl-token":
                info = inst.get("parsed", {}).get("info", {})
                mint = info.get("mint")
                if mint:
                    msg = f"🚨 PRUEBA: Recibido TOKEN_MINT, mint: {mint}"
                    print(msg)
                    res = requests.post(
                        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                        data={"chat_id": TG_CHAT, "text": msg}
                    )
                    print("Telegram test send:", res.status_code, res.text)
    return "", 200

@app.route('/')
def home():
    return "MemeRep Webhook activo 🚀"

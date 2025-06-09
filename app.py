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
    for tx in data:
        for inst in tx["transaction"]["message"]["instructions"]:
            if inst.get("program") == "spl-token":
                info = inst.get("parsed", {}).get("info", {})
                mint = info.get("mint")

                # Simulación de valores de market cap y holders (reemplazables por funciones reales)
                mc = 120_000   # market cap ficticio
                holders = 600  # número de holders ficticio

                if mc < 200_000 and holders > 500:
                    send_telegram(f"🔔 Nueva memecoin detectada:\nMint: {mint}\nMC: {mc}\nHolders: {holders}")
    return "", 200

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TG_CHAT, "text": msg})

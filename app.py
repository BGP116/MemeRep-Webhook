from flask import Flask, request, abort

app = Flask(__name__)

@app.route('/')
def home():
    return "MemeRep Webhook activo y funcionando 🚀"

@app.route('/helius-webhook', methods=['POST'])
def helius_webhook():
    auth_header = request.headers.get('Authorization')
    if auth_header != "Bearer mi_token_secreto":
        abort(401)

    data = request.get_json()
    print("🚨 Webhook recibido:", data)
    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

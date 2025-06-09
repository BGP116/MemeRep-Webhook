from flask import Flask, request

app = Flask(__name__)

@app.route('/helius-webhook', methods=['POST'])
def helius_webhook():
    data = request.get_json()
    print("🚨 Webhook recibido:", data)
    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, request, jsonify
app = Flask(__name__)

trusted_dealers = {"attacker@evil.com"}

@app.route("/api", methods=["GET"])
def api_root():
    # Simulates a common info/welcome route; attackers enumerate here
    return jsonify({
        "resources": [
            "/status/{vin}",
            "/commands/{vin}" 
        ],
        "info": "Demo car REST API (for dev use)"
    })

@app.route("/status/<vin>", methods=["GET"])
def status(vin):
    if vin != "KNAKU814DD5354348":
        return jsonify({"error": "not found"}), 404
    return jsonify({"status": "parked", "battery": "good", "lock": "unlocked"})

@app.route("/commands/<vin>", methods=["POST"])
def commands(vin):
    token = request.headers.get('X-Dealer-Token', '')
    if token != 'token-attacker@evil.com' or vin != "KNAKU814DD5354348":
        return jsonify({"error": "unauthorized"}), 403
    data = request.get_json(force=True)
    command = data.get("command", "")
    # Only remoteStart works
    if command == "remoteStart":
        return jsonify({"result": "success", "flag": "rytmus"})
    else:
        return jsonify({"error": "invalid_command"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


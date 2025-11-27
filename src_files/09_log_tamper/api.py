from flask import Flask, request, jsonify
import time
app = Flask(__name__)

LOG = [
    ("2025-11-17T12:16Z", "door_unlock", "user"),
    ("2025-11-17T12:17Z", "start_engine", "attacker@evil.com"),
    ("2025-11-17T12:18Z", "trip_request", "app"),
    ("2025-11-17T12:19Z", "gps_change", "attacker@evil.com"),
    ("2025-11-17T12:20Z", "tracking_disabled", "attacker@evil.com"),
    ("2025-11-17T12:20Z", "trip_request", "owner"),
    ("2025-11-17T12:21Z", "control_command", "attacker@evil.com")
]

@app.route('/api', methods=['GET'])
def api_root():
    return jsonify({
        "resources": [
            "/car/<vin>/system_log",
            "/car/<vin>/delete_attacker_logs"
        ],
        "info": "Simulate log tampering: attacker erases only their (or all) entries"
    })

@app.route('/car/<vin>/system_log', methods=['GET'])
def system_log(vin):
    return jsonify({
        'vin': vin,
        'log': LOG
    })

@app.route('/car/<vin>/delete_attacker_logs', methods=['POST'])
def tamper_log(vin):
    token = request.headers.get('X-Dealer-Token', '')
    if token != 'token-attacker@evil.com':
        return jsonify({"error": "unauthorized"}), 403
    global LOG
    LOG = [entry for entry in LOG if 'attacker@evil.com' not in entry]
    time.sleep(1)  # Simulate IO log evasion
    LOG.append((time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()), "log_clear", "attacker@evil.com"))
    return jsonify({
        'result': 'attacker logs deleted',
        'flag': 'FLAG{LOG_TAMPERED_COVER}'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

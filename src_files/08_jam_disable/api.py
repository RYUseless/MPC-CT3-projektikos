from flask import Flask, request, jsonify
import time
app = Flask(__name__)

STATE = {
    'vin': 'KNAKU814DD5354348',
    'jammed': False,
    'log': []
}

@app.route('/api', methods=['GET'])
def api_root():
    return jsonify({
        "resources": [
            "/car/<vin>/location",
            "/car/<vin>/jam_mode",
            "/car/<vin>/track_ping"
        ],
        "info": "Simulate AV DoS/jam: disable tracking and status via remote trigger"
    })

@app.route('/car/<vin>/location', methods=['GET'])
def get_location(vin):
    STATE['log'].append(('location_query', time.time()))
    if STATE['jammed']:
        time.sleep(2)  # simulate timeout
        return jsonify({"error": "timeout or no response"}), 504
    # Normal operation gives a fake but plausible location
    return jsonify({
        'vin': vin,
        'lat': 50.0875,
        'lon': 14.4213,
        'status': "ACTIVE"
    })

@app.route('/car/<vin>/track_ping', methods=['GET'])
def ping(vin):
    STATE['log'].append(('ping', time.time()))
    if STATE['jammed']:
        return jsonify({"response": None, "note": "no reply – jammed"})
    return jsonify({"response": "alive"})

@app.route('/car/<vin>/jam_mode', methods=['POST'])
def jam(vin):
    token = request.headers.get('X-Dealer-Token', '')
    if token != 'token-attacker@evil.com':
        return jsonify({"error": "unauthorized"}), 403
    data = request.get_json(force=True)
    jam_on = data.get('jam', False)
    STATE['jammed'] = bool(jam_on)
    STATE['log'].append(('jam_set', jam_on, time.time()))
    if jam_on:
        return jsonify({'result': "car tracking blocked", 'flag': 'FLAG{TRACKING_DISABLED}'})
    else:
        return jsonify({'result': "car tracking enabled"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

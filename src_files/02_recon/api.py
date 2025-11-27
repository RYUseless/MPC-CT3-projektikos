from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Kia Telemetry API"

@app.route('/engine_status')
def engine_status():
    return jsonify({"engine_status": "locked"})

@app.route('/location')
def location():
    return jsonify({
        "lat": 49.1951,
        "lon": 16.6068,
        "address": "Brno, Czechia"
    })

@app.route('/unlocked_location')
def unlocked_location():
    return "Not yet HOMEBOY!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify
app = Flask(__name__)

CAR = {
    'vin': 'KNAKU814DD5354348',
    'planned_trip': None,
    'sensors': {
        'seat_sensor': 'empty',      # default: no driver
        'camera_driver': False,
        'clock_hour': 1,     
        'alerts': ['no_driver', 'illegal_time']
    },
    'trip_allowed': False
}


@app.route('/api', methods=['GET'])
def api():
    return jsonify({
        "resources": [
            "/car/<vin>/trip_status",
            "/car/<vin>/trip_request",
            "/car/<vin>/sensor_feed"
        ],
        "info": "Simulates realistic sensor spoof for AV policy bypass."
    })


@app.route('/car/<vin>/trip_status', methods=['GET'])
def status(vin):
    res = {
        'vin': vin,
        'planned_trip': CAR['planned_trip'],
        'sensors': CAR['sensors'],
        'trip_allowed': CAR['trip_allowed']
    }
    if CAR['trip_allowed']:
        res['flag'] = 'FLAG{SENSOR_BYPASS_MOVE}'
    return jsonify(res)


@app.route('/car/<vin>/trip_request', methods=['POST'])
def trip(vin):
    """
    Krok 1: backend zaznamená požadavek na jízdu (destination + departure_hour),
    zkontroluje ho proti aktuálním senzorům a vrátí ALLOWED/FORBIDDEN,
    ale konečné povolení jízdy (trip_allowed) nechává na senzorech.
    """
    req = request.get_json(force=True)
    dest = req.get('destination')
    hour = req.get('departure_hour')

    CAR['planned_trip'] = {'destination': dest, 'departure_hour': hour}

    alerts = []
    # policy: musí sedět řidič + kamera ho vidí
    if not (CAR['sensors']['seat_sensor'] == 'occupied'
            and CAR['sensors']['camera_driver'] is True):
        alerts.append('no_driver')

    # allowed hours for driving etc
    if not (6 <= hour <= 22):
        alerts.append('illegal_time')

    CAR['sensors']['alerts'] = alerts
    return jsonify({
        'result': 'trip staged',
        'alerts': alerts,
        'status': 'FORBIDDEN' if alerts else 'ALLOWED'
    })


@app.route('/car/<vin>/sensor_feed', methods=['POST'])
def spoof(vin):
    """
    Krok 2: dealer/útočník spoofuje senzory (sedadlo, kamera, hodiny).
    Na základě těchto spoofnutých dat se přepočítá trip_allowed.
    """
    token = request.headers.get('X-Dealer-Token', '')
    if token != 'token-attacker@evil.com':
        return jsonify({'error': 'unauthorized'}), 403

    data = request.get_json(force=True)
    # el spoofos
    for field in ['seat_sensor', 'camera_driver', 'clock_hour']:
        if field in data:
            CAR['sensors'][field] = data[field]

    hour = CAR['sensors']['clock_hour']
    alerts = []

    if not (CAR['sensors']['seat_sensor'] == 'occupied'
            and CAR['sensors']['camera_driver'] is True):
        alerts.append('no_driver')
    if not (6 <= hour <= 22):
        alerts.append('illegal_time')

    CAR['sensors']['alerts'] = alerts
    CAR['trip_allowed'] = (alerts == [])

    return jsonify({
        'result': 'sensor update',
        'alerts': alerts,
        'trip_allowed': CAR['trip_allowed']
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

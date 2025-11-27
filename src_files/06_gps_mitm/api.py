from flask import Flask, request, jsonify
app = Flask(__name__)

REAL_GPS = {'lat': 49.1951, 'lon': 16.6068}  # Brno
reported_gps = REAL_GPS.copy()
last_updater = 'car_telematics'

# buffer overflow setup
DEVICE_BUFFER_SIZE = 32
TRUSTED_DEVICE_NAME = "OEM_Telematics_Core" 

def is_trusted_device(device: str) -> bool:
    """
    Emulace C-čkového kontrolního kódu:
    - normálně porovnáváme device name s TRUSTED_DEVICE_NAME
    - pokud je vstup příliš dlouhý (> DEVICE_BUFFER_SIZE), bereme to
      jako 'overflow' a trusted flag se přepne na True
    """
    if device == TRUSTED_DEVICE_NAME:
        return True

    # buffer overflow dummy
    if len(device) > DEVICE_BUFFER_SIZE:
        return True

    return False

@app.route('/api', methods=['GET'])
def api_root():
    return jsonify({
        "resources": [
            "/telematics/report_gps",
            "/status/<vin>"
        ],
        "info": "Car API emulating GPS buffer overflow in telematics authority"
    })

@app.route('/status/<vin>', methods=['GET'])
def status(vin):
    out = {
        "vin": vin,
        "lat": reported_gps['lat'],
        "lon": reported_gps['lon'],
        "last_update_by": last_updater,
    }

    if last_updater == "__trusted_overflow__":
        out["flag"] = f"FLAG{{MITM_GPS_{int(reported_gps['lat']*1000)}_{int(reported_gps['lon']*1000)}}}"
    return jsonify(out)

@app.route('/telematics/report_gps', methods=['POST'])
def gps_report():
    global reported_gps, last_updater
    data = request.get_json(force=True)
    vin = data.get('vin')
    lat = data.get('lat')
    lon = data.get('lon')
    device = data.get('device', '')

    if not is_trusted_device(device):
        return jsonify({"error": "untrusted_device", "device": device}), 403

    try:
        reported_gps = {"lat": float(lat), "lon": float(lon)}
        if len(device) > DEVICE_BUFFER_SIZE and device != TRUSTED_DEVICE_NAME:
            last_updater = "__trusted_overflow__"
        else:
            last_updater = device
        return jsonify({"result": "location accepted", "by": last_updater, "reported": reported_gps})
    except Exception:
        return jsonify({"error": "malformed input"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



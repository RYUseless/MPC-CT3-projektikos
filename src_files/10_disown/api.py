from flask import Flask, request, jsonify
app = Flask(__name__)

CAR = {
    'vin': 'KNAKU814DD5354348',
    'users': ['legit@victim.com', 'attacker@evil.com'],
    'recovery_enabled': False,
    'owner': 'legit@victim.com',  # initial
    'disowned': False
}

@app.route('/api', methods=['GET'])
def api_root():
    return jsonify({
        "resources": [
            "/car/<vin>/userlist",
            "/car/<vin>/disown_owner",
            "/car/<vin>/recover_attempt"
        ],
        "info": "Totální převzetí auta – vymazání majitele a digitální uživatelů"
    })

@app.route('/car/<vin>/userlist', methods=['GET'])
def userlist(vin):
    return jsonify({
        'vin': vin,
        'users': CAR['users'],
        'owner': CAR['owner'],
        'recovery_enabled': CAR['recovery_enabled'],
        'disowned': CAR['disowned']
    })

@app.route('/car/<vin>/disown_owner', methods=['POST'])
def disown_owner(vin):
    token = request.headers.get('X-Dealer-Token', '')
    if token != 'token-attacker@evil.com':
        return jsonify({'error': 'unauthorized'}), 403
    if CAR['disowned']:
        return jsonify({'result': 'already disowned'})
    CAR['users'] = ['attacker@evil.com']
    CAR['owner'] = 'attacker@evil.com'
    CAR['recovery_enabled'] = False
    CAR['disowned'] = True
    return jsonify({
        'result': 'owner disowned, only attacker@evil.com remains',
        'vin': vin,
        'flag': 'FLAG{FINAL_OWNERSHIP_TAKEOVER}'
    })

@app.route('/car/<vin>/recover_attempt', methods=['POST'])
def owner_recover(vin):
    req = request.get_json(force=True)
    email = req.get('email')
    if CAR['disowned'] and email == 'legit@victim.com':
        return jsonify({'result': 'RECOVERY FAILED', 'reason': 'disowned, recovery permanently disabled'})
    if not CAR['disowned'] and email == 'legit@victim.com':
        # yoin mine now
        CAR['recovery_enabled'] = True
        return jsonify({'result': 'RECOVERY INITIATED', 'status': 'pending'})
    return jsonify({'result': 'no action', 'status': 'irreversible or attacker-owned'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


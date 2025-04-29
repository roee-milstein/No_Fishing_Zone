from flask import Blueprint, request, jsonify

alerts_bp = Blueprint('alerts', __name__)

shared_alerts = []

@alerts_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """
    Retrieve a list of all shared alerts.
    """
    return jsonify(shared_alerts)

@alerts_bp.route('/alerts', methods=['POST'])
def post_alert():
    """
    Post a new alert shared by a user.
    Requires a JSON body with 'username' and 'message' fields.
    """
    data = request.get_json()
    username = data.get('username')
    message = data.get('message')

    if not username or not message:
        return jsonify({'error': 'Missing username or message'}), 400

    alert = {
        'username': username,
        'message': message
    }
    shared_alerts.append(alert)
    return jsonify({'status': 'Alert shared successfully'}), 201

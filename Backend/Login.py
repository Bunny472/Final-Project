# Login.py

from flask import request, jsonify, Blueprint
from models import db, User

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        return jsonify({'success': True, 'message': 'Login successful'}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

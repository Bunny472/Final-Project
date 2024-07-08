# Signup.py

from flask import request, jsonify, Blueprint
from models import db, User

signup_bp = Blueprint('signup_bp', __name__)

@signup_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()

    fullname = data.get('fullname')
    email = data.get('email')
    password = data.get('password')

    if not fullname or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'User already exists.'}), 409

    new_user = User(fullname=fullname, email=email)
    new_user.set_password(password)  # Hash the password
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Account created successfully!'}), 201

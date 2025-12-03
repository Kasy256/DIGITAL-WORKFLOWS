"""
Authentication routes - Register, Login, Profile, JWT handling
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from app import mongo
from app.models.user import User
from email_validator import validate_email, EmailNotValidError

auth_bp = Blueprint('auth', __name__)


def get_user_model():
    """Helper function to safely create User model instance"""
    try:
        return User(mongo)
    except ConnectionError as e:
        raise ConnectionError(f"MongoDB connection error: {str(e)}")


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request Body:
    {
        "email": "user@example.com",
        "password": "securepassword",
        "business_name": "My Business",
        "phone": "+1234567890" (optional)
    }
    """
    data = request.get_json()
    
    # Validation
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Validate email format
    try:
        valid = validate_email(data['email'])
        data['email'] = valid.email
    except EmailNotValidError as e:
        return jsonify({'error': f'Invalid email: {str(e)}'}), 400
    
    # Validate password strength
    if len(data['password']) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Create user
    try:
        user_model = User(mongo)
    except ConnectionError as e:
        return jsonify({
            'error': 'Database connection error',
            'message': str(e)
        }), 500
    
    user = user_model.create_user(data)
    
    if not user:
        return jsonify({'error': 'Email already registered'}), 409
    
    # Generate tokens
    access_token = create_access_token(identity=str(user['_id']))
    refresh_token = create_refresh_token(identity=str(user['_id']))
    
    return jsonify({
        'message': 'Registration successful',
        'user': User.serialize(user),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user and return JWT tokens
    
    Request Body:
    {
        "email": "user@example.com",
        "password": "securepassword"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    user_model = User(mongo)
    user = user_model.find_by_email(data['email'])
    
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.get('is_active', True):
        return jsonify({'error': 'Account is deactivated'}), 401
    
    if not user_model.verify_password(user['password'], data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Generate tokens
    access_token = create_access_token(identity=str(user['_id']))
    refresh_token = create_refresh_token(identity=str(user['_id']))
    
    return jsonify({
        'message': 'Login successful',
        'user': User.serialize(user),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token
    
    Headers:
        Authorization: Bearer <refresh_token>
    """
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        'access_token': access_token
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get current user's profile
    
    Headers:
        Authorization: Bearer <access_token>
    """
    current_user_id = get_jwt_identity()
    user_model = User(mongo)
    user = user_model.find_by_id(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': User.serialize(user)
    }), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update current user's profile
    
    Request Body:
    {
        "business_name": "New Business Name",
        "phone": "+1234567890",
        "business_address": "123 Main St",
        "settings": {
            "default_tax_rate": 15,
            "currency": "EUR"
        }
    }
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    user_model = User(mongo)
    success = user_model.update_user(current_user_id, data)
    
    if not success:
        return jsonify({'error': 'Failed to update profile'}), 400
    
    user = user_model.find_by_id(current_user_id)
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': User.serialize(user)
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change user's password
    
    Request Body:
    {
        "current_password": "oldpassword",
        "new_password": "newpassword"
    }
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current and new passwords are required'}), 400
    
    if len(data['new_password']) < 6:
        return jsonify({'error': 'New password must be at least 6 characters'}), 400
    
    user_model = User(mongo)
    user = user_model.find_by_id(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Verify current password
    if not user_model.verify_password(user['password'], data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Change password
    success = user_model.change_password(current_user_id, data['new_password'])
    
    if not success:
        return jsonify({'error': 'Failed to change password'}), 400
    
    return jsonify({
        'message': 'Password changed successfully'
    }), 200


@auth_bp.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    """
    Delete (deactivate) user account
    """
    current_user_id = get_jwt_identity()
    user_model = User(mongo)
    
    success = user_model.delete_user(current_user_id)
    
    if not success:
        return jsonify({'error': 'Failed to delete account'}), 400
    
    return jsonify({
        'message': 'Account deleted successfully'
    }), 200


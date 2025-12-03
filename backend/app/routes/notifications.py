"""
Notification routes - Send receipts via Email and SMS
"""
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.models.receipt import Receipt
from app.models.user import User
from app.services.email_service import EmailService
from app.services.sms_service import SMSService

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/send-email/<receipt_id>', methods=['POST'])
@jwt_required()
def send_email(receipt_id):
    """
    Send receipt via email
    
    URL Parameters:
        receipt_id: The ID of the receipt to send
    
    Optional Request Body:
    {
        "email": "override@example.com"  # Override customer email
    }
    """
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    # Get receipt
    receipt_model = Receipt(mongo)
    receipt = receipt_model.find_by_id(receipt_id, current_user_id)
    
    if not receipt:
        return jsonify({'error': 'Receipt not found'}), 404
    
    # Override email if provided
    if data.get('email'):
        receipt['customer_email'] = data['email']
    
    if not receipt.get('customer_email'):
        return jsonify({'error': 'No email address available for this receipt'}), 400
    
    # Get business info for branding
    user_model = User(mongo)
    user = user_model.find_by_id(current_user_id)
    business_info = {
        'business_name': user.get('business_name', 'EReceipt'),
        'business_address': user.get('business_address', ''),
    } if user else None
    
    # Send email
    success, message = EmailService.send_receipt_email(receipt, business_info)
    
    if success:
        # Mark receipt as email sent
        receipt_model.mark_email_sent(receipt_id)
        
        return jsonify({
            'success': True,
            'message': message,
            'sent_to': receipt['customer_email']
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 500


@notifications_bp.route('/send-sms/<receipt_id>', methods=['POST'])
@jwt_required()
def send_sms(receipt_id):
    """
    Send receipt via SMS
    
    URL Parameters:
        receipt_id: The ID of the receipt to send
    
    Optional Request Body:
    {
        "phone": "+1234567890"  # Override customer phone
    }
    """
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    # Get receipt
    receipt_model = Receipt(mongo)
    receipt = receipt_model.find_by_id(receipt_id, current_user_id)
    
    if not receipt:
        return jsonify({'error': 'Receipt not found'}), 404
    
    # Override phone if provided
    if data.get('phone'):
        receipt['customer_phone'] = data['phone']
    
    if not receipt.get('customer_phone'):
        return jsonify({'error': 'No phone number available for this receipt'}), 400
    
    # Get business info for branding
    user_model = User(mongo)
    user = user_model.find_by_id(current_user_id)
    business_info = {
        'business_name': user.get('business_name', 'EReceipt'),
    } if user else None
    
    # Send SMS
    success, message = SMSService.send_receipt_sms(receipt, business_info)
    
    if success:
        # Mark receipt as SMS sent
        receipt_model.mark_sms_sent(receipt_id)
        
        return jsonify({
            'success': True,
            'message': message,
            'sent_to': receipt['customer_phone']
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 500


@notifications_bp.route('/send-both/<receipt_id>', methods=['POST'])
@jwt_required()
def send_both(receipt_id):
    """
    Send receipt via both Email and SMS
    
    URL Parameters:
        receipt_id: The ID of the receipt to send
    
    Optional Request Body:
    {
        "email": "override@example.com",
        "phone": "+1234567890"
    }
    """
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    # Get receipt
    receipt_model = Receipt(mongo)
    receipt = receipt_model.find_by_id(receipt_id, current_user_id)
    
    if not receipt:
        return jsonify({'error': 'Receipt not found'}), 404
    
    # Override contact info if provided
    if data.get('email'):
        receipt['customer_email'] = data['email']
    if data.get('phone'):
        receipt['customer_phone'] = data['phone']
    
    # Get business info
    user_model = User(mongo)
    user = user_model.find_by_id(current_user_id)
    business_info = {
        'business_name': user.get('business_name', 'EReceipt'),
        'business_address': user.get('business_address', ''),
    } if user else None
    
    results = {
        'email': {'sent': False, 'message': 'No email address provided'},
        'sms': {'sent': False, 'message': 'No phone number provided'}
    }
    
    # Send email if available
    if receipt.get('customer_email'):
        email_success, email_message = EmailService.send_receipt_email(receipt, business_info)
        results['email'] = {
            'sent': email_success,
            'message': email_message,
            'sent_to': receipt['customer_email'] if email_success else None
        }
        if email_success:
            receipt_model.mark_email_sent(receipt_id)
    
    # Send SMS if available
    if receipt.get('customer_phone'):
        sms_success, sms_message = SMSService.send_receipt_sms(receipt, business_info)
        results['sms'] = {
            'sent': sms_success,
            'message': sms_message,
            'sent_to': receipt['customer_phone'] if sms_success else None
        }
        if sms_success:
            receipt_model.mark_sms_sent(receipt_id)
    
    # Determine overall success
    any_success = results['email']['sent'] or results['sms']['sent']
    
    return jsonify({
        'success': any_success,
        'results': results
    }), 200 if any_success else 500


@notifications_bp.route('/config', methods=['GET'])
@jwt_required()
def get_notification_config():
    """
    Get current notification service configuration status
    Shows which services are configured and available
    """
    email_configured = bool(
        os.getenv('MAIL_USERNAME') and os.getenv('MAIL_PASSWORD')
    )
    
    sms_config = SMSService.check_configuration()
    
    return jsonify({
        'email': {
            'configured': email_configured,
            'provider': 'Gmail SMTP' if email_configured else None
        },
        'sms': {
            'configured': sms_config.get('configured', False),
            'provider': 'Twilio' if sms_config.get('twilio') else None
        }
    }), 200


@notifications_bp.route('/test-email', methods=['POST'])
@jwt_required()
def test_email():
    """
    Send a test email to verify configuration
    
    Request Body:
    {
        "email": "test@example.com"
    }
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'error': 'Email address is required'}), 400
    
    # Get user info
    user_model = User(mongo)
    user = user_model.find_by_id(current_user_id)
    business_info = {
        'business_name': user.get('business_name', 'EReceipt'),
    } if user else None
    
    # Create test receipt
    test_receipt = {
        'receipt_number': 'TEST-001',
        'customer_name': 'Test Customer',
        'customer_email': data['email'],
        'transaction_date': '2025-12-03',
        'items': [
            {'name': 'Test Item 1', 'quantity': 1, 'price': 10.00},
            {'name': 'Test Item 2', 'quantity': 2, 'price': 5.00}
        ],
        'subtotal': 20.00,
        'tax_rate': 10,
        'tax': 2.00,
        'total': 22.00
    }
    
    success, message = EmailService.send_receipt_email(test_receipt, business_info)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 500


@notifications_bp.route('/test-sms', methods=['POST'])
@jwt_required()
def test_sms():
    """
    Send a test SMS to verify configuration
    
    Request Body:
    {
        "phone": "+1234567890"
    }
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('phone'):
        return jsonify({'error': 'Phone number is required'}), 400
    
    # Get user info
    user_model = User(mongo)
    user = user_model.find_by_id(current_user_id)
    business_info = {
        'business_name': user.get('business_name', 'EReceipt'),
    } if user else None
    
    # Create test receipt
    test_receipt = {
        'receipt_number': 'TEST-001',
        'customer_name': 'Test Customer',
        'customer_phone': data['phone'],
        'transaction_date': '2025-12-03',
        'total': 22.00
    }
    
    success, message = SMSService.send_receipt_sms(test_receipt, business_info)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 500




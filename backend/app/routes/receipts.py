"""
Receipt routes - CRUD operations for receipts
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.models.receipt import Receipt

receipts_bp = Blueprint('receipts', __name__)


@receipts_bp.route('', methods=['POST'])
@jwt_required()
def create_receipt():
    """
    Create a new receipt
    
    Request Body:
    {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "customer_phone": "+1234567890",
        "transaction_date": "2025-12-03",
        "items": [
            {"name": "Product 1", "quantity": 2, "price": 29.99},
            {"name": "Product 2", "quantity": 1, "price": 49.99}
        ],
        "subtotal": 109.97,
        "tax_rate": 10,
        "tax": 10.99,
        "total": 120.96,
        "payment_method": "Card",
        "notes": "Customer notes"
    }
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validation
    required_fields = ['customer_name', 'items', 'subtotal', 'tax', 'total']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    if not data['items'] or not isinstance(data['items'], list):
        return jsonify({'error': 'Items must be a non-empty list'}), 400
    
    # Validate items
    for i, item in enumerate(data['items']):
        if not item.get('name'):
            return jsonify({'error': f'Item {i+1} is missing name'}), 400
        if not isinstance(item.get('quantity'), (int, float)) or item['quantity'] <= 0:
            return jsonify({'error': f'Item {i+1} has invalid quantity'}), 400
        if not isinstance(item.get('price'), (int, float)) or item['price'] < 0:
            return jsonify({'error': f'Item {i+1} has invalid price'}), 400
    
    receipt_model = Receipt(mongo)
    receipt = receipt_model.create_receipt(current_user_id, data)
    
    return jsonify({
        'message': 'Receipt created successfully',
        'receipt': Receipt.serialize(receipt)
    }), 201


@receipts_bp.route('', methods=['GET'])
@jwt_required()
def get_receipts():
    """
    Get all receipts for current user with pagination
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)
        search: Search term
        status: Filter by status (created, email_sent, sms_sent, both_sent)
    """
    current_user_id = get_jwt_identity()
    
    # Parse query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    search = request.args.get('search', None)
    status = request.args.get('status', None)
    
    if page < 1:
        page = 1
    
    receipt_model = Receipt(mongo)
    receipts, total = receipt_model.find_by_user(
        current_user_id,
        page=page,
        per_page=per_page,
        search=search,
        status=status
    )
    
    return jsonify({
        'receipts': [Receipt.serialize(r) for r in receipts],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    }), 200


@receipts_bp.route('/<receipt_id>', methods=['GET'])
@jwt_required()
def get_receipt(receipt_id):
    """
    Get a single receipt by ID
    """
    current_user_id = get_jwt_identity()
    receipt_model = Receipt(mongo)
    
    receipt = receipt_model.find_by_id(receipt_id, current_user_id)
    
    if not receipt:
        return jsonify({'error': 'Receipt not found'}), 404
    
    return jsonify({
        'receipt': Receipt.serialize(receipt)
    }), 200


@receipts_bp.route('/number/<receipt_number>', methods=['GET'])
@jwt_required()
def get_receipt_by_number(receipt_number):
    """
    Get a single receipt by receipt number
    """
    current_user_id = get_jwt_identity()
    receipt_model = Receipt(mongo)
    
    receipt = receipt_model.find_by_receipt_number(receipt_number, current_user_id)
    
    if not receipt:
        return jsonify({'error': 'Receipt not found'}), 404
    
    return jsonify({
        'receipt': Receipt.serialize(receipt)
    }), 200


@receipts_bp.route('/<receipt_id>', methods=['PUT'])
@jwt_required()
def update_receipt(receipt_id):
    """
    Update a receipt
    
    Request Body: Same as create, but all fields optional
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    receipt_model = Receipt(mongo)
    
    # Check if receipt exists
    existing = receipt_model.find_by_id(receipt_id, current_user_id)
    if not existing:
        return jsonify({'error': 'Receipt not found'}), 404
    
    # Update receipt
    success = receipt_model.update_receipt(receipt_id, current_user_id, data)
    
    if not success:
        return jsonify({'error': 'Failed to update receipt'}), 400
    
    # Get updated receipt
    receipt = receipt_model.find_by_id(receipt_id, current_user_id)
    
    return jsonify({
        'message': 'Receipt updated successfully',
        'receipt': Receipt.serialize(receipt)
    }), 200


@receipts_bp.route('/<receipt_id>', methods=['DELETE'])
@jwt_required()
def delete_receipt(receipt_id):
    """
    Delete a receipt
    """
    current_user_id = get_jwt_identity()
    receipt_model = Receipt(mongo)
    
    # Check if receipt exists
    existing = receipt_model.find_by_id(receipt_id, current_user_id)
    if not existing:
        return jsonify({'error': 'Receipt not found'}), 404
    
    success = receipt_model.delete_receipt(receipt_id, current_user_id)
    
    if not success:
        return jsonify({'error': 'Failed to delete receipt'}), 400
    
    return jsonify({
        'message': 'Receipt deleted successfully'
    }), 200


@receipts_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """
    Get receipt statistics for current user
    """
    current_user_id = get_jwt_identity()
    receipt_model = Receipt(mongo)
    
    stats = receipt_model.get_stats(current_user_id)
    
    return jsonify({
        'stats': stats
    }), 200


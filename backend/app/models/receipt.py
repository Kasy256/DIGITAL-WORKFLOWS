"""
Receipt model for storing and managing receipts
"""
from datetime import datetime
from bson import ObjectId


class Receipt:
    """Receipt model for MongoDB"""
    
    collection_name = 'receipts'
    
    def __init__(self, mongo):
        self.collection = mongo.db[self.collection_name]
    
    def create_receipt(self, user_id, data):
        """
        Create a new receipt
        
        Args:
            user_id: Owner's user ID
            data: Receipt data including customer info, items, totals
        
        Returns:
            Created receipt document
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        # Generate receipt number
        receipt_number = f"REC-{datetime.utcnow().strftime('%Y%m%d')}-{ObjectId()}"[:20]
        
        receipt_doc = {
            'user_id': user_id,
            'receipt_number': data.get('receipt_number', receipt_number),
            
            # Customer Information
            'customer_name': data['customer_name'],
            'customer_email': data.get('customer_email', ''),
            'customer_phone': data.get('customer_phone', ''),
            
            # Transaction Details
            'transaction_date': data.get('transaction_date', datetime.utcnow().strftime('%Y-%m-%d')),
            'items': data['items'],  # List of {name, quantity, price}
            
            # Financial Details
            'subtotal': float(data['subtotal']),
            'tax_rate': float(data.get('tax_rate', 10)),
            'tax': float(data['tax']),
            'total': float(data['total']),
            'currency': data.get('currency', 'USD'),
            
            # Payment Information
            'payment_method': data.get('payment_method', 'Cash'),
            'payment_status': data.get('payment_status', 'Paid'),
            
            # Delivery Status
            'status': 'created',  # created, email_sent, sms_sent, both_sent
            'email_sent': False,
            'email_sent_at': None,
            'sms_sent': False,
            'sms_sent_at': None,
            
            # Notes
            'notes': data.get('notes', ''),
            
            # Metadata
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.collection.insert_one(receipt_doc)
        receipt_doc['_id'] = result.inserted_id
        return receipt_doc
    
    def find_by_id(self, receipt_id, user_id=None):
        """Find receipt by ID, optionally verify ownership"""
        if isinstance(receipt_id, str):
            receipt_id = ObjectId(receipt_id)
        
        query = {'_id': receipt_id}
        if user_id:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            query['user_id'] = user_id
        
        return self.collection.find_one(query)
    
    def find_by_receipt_number(self, receipt_number, user_id=None):
        """Find receipt by receipt number"""
        query = {'receipt_number': receipt_number}
        if user_id:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            query['user_id'] = user_id
        
        return self.collection.find_one(query)
    
    def find_by_user(self, user_id, page=1, per_page=20, search=None, status=None):
        """
        Find all receipts for a user with pagination
        
        Args:
            user_id: User's ID
            page: Page number (1-indexed)
            per_page: Items per page
            search: Search term for customer name or receipt number
            status: Filter by status
        
        Returns:
            Tuple of (receipts list, total count)
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        query = {'user_id': user_id}
        
        # Add search filter
        if search:
            query['$or'] = [
                {'customer_name': {'$regex': search, '$options': 'i'}},
                {'receipt_number': {'$regex': search, '$options': 'i'}},
                {'customer_email': {'$regex': search, '$options': 'i'}}
            ]
        
        # Add status filter
        if status:
            query['status'] = status
        
        # Get total count
        total = self.collection.count_documents(query)
        
        # Get paginated results
        skip = (page - 1) * per_page
        receipts = list(
            self.collection.find(query)
            .sort('created_at', -1)
            .skip(skip)
            .limit(per_page)
        )
        
        return receipts, total
    
    def update_receipt(self, receipt_id, user_id, data):
        """Update receipt"""
        if isinstance(receipt_id, str):
            receipt_id = ObjectId(receipt_id)
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        # Fields that can be updated
        allowed_fields = [
            'customer_name', 'customer_email', 'customer_phone',
            'transaction_date', 'items', 'subtotal', 'tax_rate',
            'tax', 'total', 'payment_method', 'payment_status', 'notes'
        ]
        
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        update_data['updated_at'] = datetime.utcnow()
        
        result = self.collection.update_one(
            {'_id': receipt_id, 'user_id': user_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def mark_email_sent(self, receipt_id):
        """Mark receipt as email sent"""
        if isinstance(receipt_id, str):
            receipt_id = ObjectId(receipt_id)
        
        self.collection.update_one(
            {'_id': receipt_id},
            {
                '$set': {
                    'email_sent': True,
                    'email_sent_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            }
        )
        self._update_status(receipt_id)
    
    def mark_sms_sent(self, receipt_id):
        """Mark receipt as SMS sent"""
        if isinstance(receipt_id, str):
            receipt_id = ObjectId(receipt_id)
        
        self.collection.update_one(
            {'_id': receipt_id},
            {
                '$set': {
                    'sms_sent': True,
                    'sms_sent_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            }
        )
        self._update_status(receipt_id)
    
    def _update_status(self, receipt_id):
        """Update the overall status based on send states"""
        receipt = self.find_by_id(receipt_id)
        if not receipt:
            return
        
        email_sent = receipt.get('email_sent', False)
        sms_sent = receipt.get('sms_sent', False)
        
        if email_sent and sms_sent:
            status = 'both_sent'
        elif email_sent:
            status = 'email_sent'
        elif sms_sent:
            status = 'sms_sent'
        else:
            status = 'created'
        
        self.collection.update_one(
            {'_id': receipt_id},
            {'$set': {'status': status}}
        )
    
    def delete_receipt(self, receipt_id, user_id):
        """Delete receipt"""
        if isinstance(receipt_id, str):
            receipt_id = ObjectId(receipt_id)
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        result = self.collection.delete_one({
            '_id': receipt_id,
            'user_id': user_id
        })
        return result.deleted_count > 0
    
    def get_stats(self, user_id):
        """Get receipt statistics for a user"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        pipeline = [
            {'$match': {'user_id': user_id}},
            {'$group': {
                '_id': None,
                'total_receipts': {'$sum': 1},
                'total_revenue': {'$sum': '$total'},
                'total_tax': {'$sum': '$tax'},
                'emails_sent': {'$sum': {'$cond': ['$email_sent', 1, 0]}},
                'sms_sent': {'$sum': {'$cond': ['$sms_sent', 1, 0]}}
            }}
        ]
        
        result = list(self.collection.aggregate(pipeline))
        
        if result:
            stats = result[0]
            del stats['_id']
            return stats
        
        return {
            'total_receipts': 0,
            'total_revenue': 0,
            'total_tax': 0,
            'emails_sent': 0,
            'sms_sent': 0
        }
    
    @staticmethod
    def serialize(receipt):
        """Serialize receipt document for JSON response"""
        if not receipt:
            return None
        
        return {
            'id': str(receipt['_id']),
            'receipt_number': receipt['receipt_number'],
            'customer_name': receipt['customer_name'],
            'customer_email': receipt.get('customer_email', ''),
            'customer_phone': receipt.get('customer_phone', ''),
            'transaction_date': receipt['transaction_date'],
            'items': receipt['items'],
            'subtotal': receipt['subtotal'],
            'tax_rate': receipt['tax_rate'],
            'tax': receipt['tax'],
            'total': receipt['total'],
            'currency': receipt.get('currency', 'USD'),
            'payment_method': receipt.get('payment_method', 'Cash'),
            'payment_status': receipt.get('payment_status', 'Paid'),
            'status': receipt['status'],
            'email_sent': receipt.get('email_sent', False),
            'email_sent_at': receipt['email_sent_at'].isoformat() if receipt.get('email_sent_at') else None,
            'sms_sent': receipt.get('sms_sent', False),
            'sms_sent_at': receipt['sms_sent_at'].isoformat() if receipt.get('sms_sent_at') else None,
            'notes': receipt.get('notes', ''),
            'created_at': receipt['created_at'].isoformat() if receipt.get('created_at') else None,
            'updated_at': receipt['updated_at'].isoformat() if receipt.get('updated_at') else None
        }


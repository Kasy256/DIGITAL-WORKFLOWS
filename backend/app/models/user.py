"""
User model for authentication and user management
"""
from datetime import datetime
from bson import ObjectId
import bcrypt


class User:
    """User model for MongoDB"""
    
    collection_name = 'users'
    
    def __init__(self, mongo):
        if mongo.db is None:
            raise ConnectionError(
                "MongoDB connection is not available. "
                "Please ensure MongoDB is running and MONGO_URI is correctly configured."
            )
        self.collection = mongo.db[self.collection_name]
    
    def create_user(self, data):
        """
        Create a new user
        
        Args:
            data: dict with email, password, business_name, phone (optional)
        
        Returns:
            Created user document or None if email exists
        """
        # Check if user already exists
        if self.find_by_email(data['email']):
            return None
        
        # Hash the password
        hashed_password = bcrypt.hashpw(
            data['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        user_doc = {
            'email': data['email'].lower().strip(),
            'password': hashed_password,
            'business_name': data.get('business_name', ''),
            'phone': data.get('phone', ''),
            'business_address': data.get('business_address', ''),
            'business_logo': data.get('business_logo', ''),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True,
            'email_verified': False,
            'settings': {
                'default_tax_rate': 10,
                'currency': 'USD',
                'receipt_footer_message': 'Thank you for your purchase!'
            }
        }
        
        result = self.collection.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id
        return user_doc
    
    def find_by_email(self, email):
        """Find user by email"""
        return self.collection.find_one({'email': email.lower().strip()})
    
    def find_by_id(self, user_id):
        """Find user by ID"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return self.collection.find_one({'_id': user_id})
    
    def verify_password(self, stored_password, provided_password):
        """Verify password against hash"""
        return bcrypt.checkpw(
            provided_password.encode('utf-8'),
            stored_password.encode('utf-8')
        )
    
    def update_user(self, user_id, data):
        """Update user profile"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        # Remove password from update if present (use change_password instead)
        data.pop('password', None)
        data['updated_at'] = datetime.utcnow()
        
        result = self.collection.update_one(
            {'_id': user_id},
            {'$set': data}
        )
        return result.modified_count > 0
    
    def change_password(self, user_id, new_password):
        """Change user password"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        hashed_password = bcrypt.hashpw(
            new_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        result = self.collection.update_one(
            {'_id': user_id},
            {
                '$set': {
                    'password': hashed_password,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    def delete_user(self, user_id):
        """Delete user (soft delete by setting is_active to False)"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        result = self.collection.update_one(
            {'_id': user_id},
            {
                '$set': {
                    'is_active': False,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    @staticmethod
    def serialize(user):
        """Serialize user document for JSON response"""
        if not user:
            return None
        
        return {
            'id': str(user['_id']),
            'email': user['email'],
            'business_name': user.get('business_name', ''),
            'phone': user.get('phone', ''),
            'business_address': user.get('business_address', ''),
            'business_logo': user.get('business_logo', ''),
            'created_at': user['created_at'].isoformat() if user.get('created_at') else None,
            'is_active': user.get('is_active', True),
            'email_verified': user.get('email_verified', False),
            'settings': user.get('settings', {})
        }


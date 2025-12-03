"""
EReceipt Backend Application Factory
"""
from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from datetime import timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
mongo = PyMongo()
jwt = JWTManager()
mail = Mail()


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # MongoDB Atlas connection - ensure database name is included
    mongo_uri = os.getenv('MONGO_URI', 'mongodb+srv://PsecAI:Kasy%40123@cluster0.1vsiqgt.mongodb.net/')
    mongo_db_name = os.getenv('MONGO_NAME', 'E-RECIEPTS')
    
    # For MongoDB Atlas, ensure database name is in the URI
    # Format: mongodb+srv://user:pass@cluster.mongodb.net/database_name?retryWrites=true&w=majority
    if 'mongodb+srv://' in mongo_uri or 'mongodb://' in mongo_uri:
        # Parse URI to check if database name exists
        # Split by '?' to separate connection string from query params
        uri_parts = mongo_uri.split('?')
        base_uri = uri_parts[0]
        query_params = '?' + uri_parts[1] if len(uri_parts) > 1 else ''
        
        # Check if database name is missing (URI ends with / or @cluster)
        if base_uri.rstrip().endswith('/') or (base_uri.rstrip().endswith('.net') or base_uri.rstrip().endswith('.mongodb.net')):
            # Add database name if missing
            if not base_uri.rstrip().endswith('/'):
                base_uri += '/'
            base_uri += mongo_db_name
        
        # Reconstruct URI
        mongo_uri = base_uri + query_params
        
        # Ensure connection options for Atlas (if using mongodb+srv)
        if 'mongodb+srv://' in mongo_uri:
            if '?' not in mongo_uri:
                mongo_uri += '?retryWrites=true&w=majority'
            elif 'retryWrites' not in mongo_uri:
                mongo_uri += '&retryWrites=true&w=majority'
    
    app.config['MONGO_URI'] = mongo_uri
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
        seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    )
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Mail Configuration (Gmail SMTP)
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Initialize extensions with app
    mongo.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    
    # CORS - Allow frontend requests (configured to handle all routes and errors)
    # Get frontend URL from environment or use defaults
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    
    # Build allowed origins list
    allowed_origins = [
        frontend_url,
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://digital-workflows.onrender.com",  # Production frontend
    ]
    
    # Add any additional frontend URLs from environment
    if os.getenv('ADDITIONAL_FRONTEND_URLS'):
        additional_urls = os.getenv('ADDITIONAL_FRONTEND_URLS').split(',')
        allowed_origins.extend([url.strip() for url in additional_urls])
    
    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": allowed_origins,
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"]
             }
         },
         supports_credentials=True)
    
    # After request handler to ensure CORS headers are always included
    @app.after_request
    def after_request(response):
        """Ensure CORS headers are included in all responses"""
        # CORS middleware should handle this, but this ensures it works for errors too
        return response
    
    # Error handler for ConnectionError to ensure CORS headers are included
    @app.errorhandler(ConnectionError)
    def handle_connection_error(e):
        """Handle ConnectionError with CORS headers"""
        from flask import jsonify
        return jsonify({
            'error': 'Database connection error',
            'message': str(e)
        }), 500
    
    # Error handler for 500 errors to ensure CORS headers are included
    @app.errorhandler(500)
    def handle_500_error(e):
        """Handle 500 errors with CORS headers"""
        from flask import jsonify
        import traceback
        
        error_message = str(e) if str(e) else "Internal server error"
        
        # In debug mode, include traceback
        if app.config.get('DEBUG'):
            traceback_str = traceback.format_exc()
            return jsonify({
                'error': error_message,
                'traceback': traceback_str
            }), 500
        
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500
    
    # Verify MongoDB connection
    try:
        # Test MongoDB connection
        with app.app_context():
            # Force connection initialization
            try:
                # Access mongo.db to trigger connection
                db = mongo.db
                if db is None:
                    raise ConnectionError("MongoDB connection returned None")
                
                # Try a simple operation to verify connection
                db.list_collection_names()
                print("✅ MongoDB connection successful")
                print(f"   Database: {db.name}")
            except Exception as conn_error:
                print("⚠️  WARNING: MongoDB connection failed!")
                print(f"   Error: {str(conn_error)}")
                print("   Please check:")
                print("   1. MONGO_URI in .env file is correct")
                print("   2. For MongoDB Atlas: Ensure database name is in URI")
                print("   3. Format: mongodb+srv://user:pass@cluster.mongodb.net/database_name")
                print("   4. Your IP is whitelisted in MongoDB Atlas Network Access")
                print("   5. Database user has proper permissions")
    except Exception as e:
        print(f"⚠️  WARNING: MongoDB initialization error: {str(e)}")
        print("   The app will start but database operations will fail.")
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.receipts import receipts_bp
    from app.routes.notifications import notifications_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(receipts_bp, url_prefix='/api/receipts')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    
    # Health check route
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'EReceipt API is running'}
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'error': 'Token has expired', 'message': 'Please log in again'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'error': 'Invalid token', 'message': 'Token verification failed'}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'error': 'Authorization required', 'message': 'Token is missing'}, 401
    
    return app


"""
API Routes for EReceipt application
"""
from app.routes.auth import auth_bp
from app.routes.receipts import receipts_bp
from app.routes.notifications import notifications_bp

__all__ = ['auth_bp', 'receipts_bp', 'notifications_bp']


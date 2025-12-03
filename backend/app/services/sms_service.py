"""
SMS Service - Twilio SMS Integration

Uses Twilio for SMS delivery ($15 free trial credit)
Sign up at: https://www.twilio.com/try-twilio
"""
import os
from typing import Tuple


class SMSService:
    """
    SMS service for sending receipt notifications via Twilio
    """
    
    @staticmethod
    def send_receipt_sms(receipt, business_info=None) -> Tuple[bool, str]:
        """
        Send receipt notification via SMS using Twilio
        
        Args:
            receipt: Receipt document with customer_phone
            business_info: Optional business details
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        phone = receipt.get('customer_phone')
        if not phone:
            return False, "No customer phone number provided"
        
        # Clean phone number
        phone = SMSService._clean_phone_number(phone)
        if not phone:
            return False, "Invalid phone number format"
        
        # Build SMS message
        message = SMSService._build_sms_message(receipt, business_info)
        
        # Send via Twilio
        return SMSService._send_via_twilio(phone, message)
    
    @staticmethod
    def _clean_phone_number(phone: str) -> str:
        """Clean and validate phone number"""
        if not phone:
            return ""
        
        # Remove spaces, dashes, parentheses
        cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # Ensure it starts with + for international format
        if not cleaned.startswith('+'):
            # Assume US number if no country code
            if len(cleaned) == 10:
                cleaned = '+1' + cleaned
            elif len(cleaned) == 11 and cleaned.startswith('1'):
                cleaned = '+' + cleaned
        
        # Basic validation - should have at least 10 digits
        digits = ''.join(c for c in cleaned if c.isdigit())
        if len(digits) < 10:
            return ""
        
        return cleaned
    
    @staticmethod
    def _build_sms_message(receipt, business_info=None) -> str:
        """Build SMS message for receipt"""
        business_name = business_info.get('business_name', 'EReceipt') if business_info else 'EReceipt'
        
        # SMS has 160 character limit for single message
        # Keep it concise
        message = f"""
🧾 {business_name}
Receipt: {receipt['receipt_number']}
Total: ${receipt['total']:.2f}
Date: {receipt['transaction_date']}

Thank you for your purchase!
♻️ Paperless Receipt
        """.strip()
        
        # Truncate if too long
        if len(message) > 160:
            message = message[:157] + "..."
        
        return message
    
    @staticmethod
    def _send_via_twilio(phone: str, message: str) -> Tuple[bool, str]:
        """
        Send SMS using Twilio
        
        Setup:
        1. Sign up at https://www.twilio.com/try-twilio
        2. Get $15 free trial credit
        3. Get Account SID, Auth Token, and a phone number
        4. Set environment variables
        """
        try:
            from twilio.rest import Client
            
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            from_number = os.getenv('TWILIO_PHONE_NUMBER')
            
            if not all([account_sid, auth_token, from_number]):
                return False, "Twilio credentials not fully configured"
            
            client = Client(account_sid, auth_token)
            
            result = client.messages.create(
                body=message,
                from_=from_number,
                to=phone
            )
            
            return True, f"SMS sent successfully via Twilio (SID: {result.sid})"
            
        except ImportError:
            return False, "Twilio library not installed. Run: pip install twilio"
        except Exception as e:
            return False, f"Twilio error: {str(e)}"
    
    @staticmethod
    def check_configuration() -> dict:
        """Check if Twilio is configured"""
        return {
            'twilio': bool(os.getenv('TWILIO_ACCOUNT_SID') and os.getenv('TWILIO_AUTH_TOKEN')),
            'configured': bool(os.getenv('TWILIO_ACCOUNT_SID'))
        }


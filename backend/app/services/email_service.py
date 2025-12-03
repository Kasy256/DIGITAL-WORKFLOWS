"""
Email Service - Free email sending using Gmail SMTP or Flask-Mail
"""
import os
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask import current_app
from flask_mail import Message
from app import mail
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending receipt notifications
    Uses Gmail SMTP (free) or any SMTP server
    
    Setup for Gmail:
    1. Enable 2-Factor Authentication on your Google Account
    2. Generate an App Password: Google Account > Security > App Passwords
    3. Use the App Password in MAIL_PASSWORD env variable
    """
    
    @staticmethod
    def send_receipt_email(receipt, business_info=None):
        """
        Send receipt via email
        
        Args:
            receipt: Receipt document with customer_email
            business_info: Optional business details for branding
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not receipt.get('customer_email'):
            return False, "No customer email provided"
        
        try:
            # Build email content
            subject = f"Your Receipt - {receipt['receipt_number']}"
            html_body = EmailService._build_receipt_html(receipt, business_info)
            text_body = EmailService._build_receipt_text(receipt, business_info)
            
            # Check if email service is configured
            mail_username = current_app.config.get('MAIL_USERNAME') or os.getenv('MAIL_USERNAME')
            mail_password = current_app.config.get('MAIL_PASSWORD') or os.getenv('MAIL_PASSWORD')
            
            if not mail_username or not mail_password:
                logger.error("Email service not configured: Missing MAIL_USERNAME or MAIL_PASSWORD")
                return False, "Email service not configured. Please check your environment variables."
            
            # Try Flask-Mail first
            return EmailService._send_via_flask_mail(
                to_email=receipt['customer_email'],
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
                
        except socket.timeout as e:
            logger.error(f"Email send timeout: {str(e)}")
            return False, f"Email sending timed out. Please try again later."
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return False, f"Email service error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}", exc_info=True)
            return False, f"Failed to send email: {str(e)}"
    
    @staticmethod
    def _send_via_flask_mail(to_email, subject, html_body, text_body):
        """Send email using Flask-Mail with timeout handling"""
        try:
            # Set socket timeout for SMTP operations (30 seconds)
            socket.setdefaulttimeout(30)
            
            msg = Message(
                subject=subject,
                recipients=[to_email],
                html=html_body,
                body=text_body
            )
            
            # Send email with timeout protection
            mail.send(msg)
            logger.info(f"Email sent successfully to {to_email}")
            return True, "Email sent successfully"
            
        except socket.timeout as e:
            logger.error(f"Email send timeout for {to_email}: {str(e)}")
            return False, f"Email sending timed out. The SMTP server took too long to respond."
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {str(e)}")
            return False, "Email authentication failed. Please check your email credentials."
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error for {to_email}: {str(e)}")
            return False, f"Email service error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected Flask-Mail error for {to_email}: {str(e)}", exc_info=True)
            return False, f"Failed to send email: {str(e)}"
        finally:
            # Reset socket timeout to default
            socket.setdefaulttimeout(None)
    
    @staticmethod
    def _send_via_smtp(to_email, subject, html_body, text_body):
        """
        Send email using direct SMTP connection
        Alternative method if Flask-Mail has issues
        """
        try:
            smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('MAIL_PORT', 587))
            username = os.getenv('MAIL_USERNAME')
            password = os.getenv('MAIL_PASSWORD')
            sender = os.getenv('MAIL_DEFAULT_SENDER', username)
            
            if not username or not password:
                return False, "SMTP credentials not configured"
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = to_email
            
            # Attach text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Connect and send with timeout
            with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
                server.starttls()
                server.login(username, password)
                server.sendmail(sender, to_email, msg.as_string())
            
            logger.info(f"Email sent successfully via SMTP to {to_email}")
            return True, "Email sent successfully via SMTP"
            
        except socket.timeout as e:
            logger.error(f"SMTP timeout for {to_email}: {str(e)}")
            return False, f"Email sending timed out. The SMTP server took too long to respond."
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {str(e)}")
            return False, "Email authentication failed. Please check your email credentials."
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error for {to_email}: {str(e)}")
            return False, f"Email service error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected SMTP error for {to_email}: {str(e)}", exc_info=True)
            return False, f"SMTP error: {str(e)}"
    
    @staticmethod
    def _build_receipt_html(receipt, business_info=None):
        """Build HTML email content for receipt"""
        business_name = business_info.get('business_name', 'EReceipt') if business_info else 'EReceipt'
        
        items_html = ""
        for item in receipt['items']:
            item_total = item['quantity'] * item['price']
            items_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">{item['name']}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: center;">{item['quantity']}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: right;">${item['price']:.2f}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: 600;">${item_total:.2f}</td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f3f4f6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px;">🧾 {business_name}</h1>
                    <p style="margin: 8px 0 0; opacity: 0.9;">Digital Receipt</p>
                </div>
                
                <!-- Receipt Content -->
                <div style="background: white; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <!-- Receipt Number & Date -->
                    <div style="display: flex; justify-content: space-between; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 2px solid #10b981;">
                        <div>
                            <p style="margin: 0; color: #6b7280; font-size: 12px; text-transform: uppercase;">Receipt Number</p>
                            <p style="margin: 4px 0 0; font-size: 18px; font-weight: 700; color: #10b981;">{receipt['receipt_number']}</p>
                        </div>
                        <div style="text-align: right;">
                            <p style="margin: 0; color: #6b7280; font-size: 12px; text-transform: uppercase;">Date</p>
                            <p style="margin: 4px 0 0; font-size: 16px; font-weight: 600;">{receipt['transaction_date']}</p>
                        </div>
                    </div>
                    
                    <!-- Customer Info -->
                    <div style="margin-bottom: 24px;">
                        <p style="margin: 0; color: #6b7280; font-size: 12px; text-transform: uppercase;">Bill To</p>
                        <p style="margin: 4px 0 0; font-size: 16px; font-weight: 600;">{receipt['customer_name']}</p>
                        <p style="margin: 2px 0 0; color: #6b7280;">{receipt.get('customer_email', '')}</p>
                    </div>
                    
                    <!-- Items Table -->
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px;">
                        <thead>
                            <tr style="background-color: #f9fafb;">
                                <th style="padding: 12px; text-align: left; border-bottom: 2px solid #10b981; color: #374151; font-size: 12px; text-transform: uppercase;">Item</th>
                                <th style="padding: 12px; text-align: center; border-bottom: 2px solid #10b981; color: #374151; font-size: 12px; text-transform: uppercase;">Qty</th>
                                <th style="padding: 12px; text-align: right; border-bottom: 2px solid #10b981; color: #374151; font-size: 12px; text-transform: uppercase;">Price</th>
                                <th style="padding: 12px; text-align: right; border-bottom: 2px solid #10b981; color: #374151; font-size: 12px; text-transform: uppercase;">Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    
                    <!-- Totals -->
                    <div style="text-align: right; padding-top: 16px; border-top: 1px solid #e5e7eb;">
                        <div style="margin-bottom: 8px;">
                            <span style="color: #6b7280;">Subtotal:</span>
                            <span style="margin-left: 16px; font-weight: 600;">${receipt['subtotal']:.2f}</span>
                        </div>
                        <div style="margin-bottom: 12px;">
                            <span style="color: #6b7280;">Tax ({receipt['tax_rate']}%):</span>
                            <span style="margin-left: 16px; font-weight: 600;">${receipt['tax']:.2f}</span>
                        </div>
                        <div style="background-color: #d1fae5; padding: 12px 16px; border-radius: 8px; display: inline-block;">
                            <span style="font-size: 18px; font-weight: 700; color: #059669;">Total: ${receipt['total']:.2f}</span>
                        </div>
                    </div>
                    
                    <!-- Footer -->
                    <div style="margin-top: 32px; padding-top: 24px; border-top: 1px solid #e5e7eb; text-align: center;">
                        <p style="margin: 0; color: #6b7280; font-size: 14px;">Thank you for your purchase!</p>
                        <p style="margin: 8px 0 0; color: #10b981; font-size: 12px; font-weight: 600;">♻️ This is a paperless digital receipt</p>
                    </div>
                </div>
                
                <!-- Footer Note -->
                <div style="text-align: center; padding: 20px; color: #9ca3af; font-size: 12px;">
                    <p style="margin: 0;">This email was sent from {business_name}</p>
                    <p style="margin: 4px 0 0;">Powered by EReceipt - Go Paperless 🌱</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    @staticmethod
    def _build_receipt_text(receipt, business_info=None):
        """Build plain text email content for receipt"""
        business_name = business_info.get('business_name', 'EReceipt') if business_info else 'EReceipt'
        
        items_text = ""
        for item in receipt['items']:
            item_total = item['quantity'] * item['price']
            items_text += f"  - {item['name']} x{item['quantity']} @ ${item['price']:.2f} = ${item_total:.2f}\n"
        
        text = f"""
========================================
{business_name} - Digital Receipt
========================================

Receipt Number: {receipt['receipt_number']}
Date: {receipt['transaction_date']}

Customer: {receipt['customer_name']}
Email: {receipt.get('customer_email', 'N/A')}

----------------------------------------
ITEMS:
{items_text}
----------------------------------------

Subtotal: ${receipt['subtotal']:.2f}
Tax ({receipt['tax_rate']}%): ${receipt['tax']:.2f}
----------------------------------------
TOTAL: ${receipt['total']:.2f}
----------------------------------------

Thank you for your purchase!
This is a paperless digital receipt.

Powered by EReceipt - Go Paperless 🌱
========================================
        """
        return text.strip()


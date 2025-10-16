"""
Email service for sending verification and notification emails
"""
import os
import logging
from flask import current_app
from flask_mail import Message, Mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

logger = logging.getLogger(__name__)


class EmailService:
    """Handle email sending operations"""
    
    def __init__(self):
        """Initialize email service"""
        self.mail = None
        self.serializer = None
    
    def _get_mail_instance(self):
        """Get Flask-Mail instance from current_app"""
        if self.mail is None:
            try:
                self.mail = Mail(current_app)
            except RuntimeError:
                logger.error("Could not get Mail instance - no application context")
                raise
        return self.mail
    
    def _get_serializer(self):
        """Get URL serializer for token generation"""
        if self.serializer is None:
            secret_key = current_app.config.get('SECRET_KEY') or os.environ.get('SECRET_KEY', 'dev-secret-key')
            self.serializer = URLSafeTimedSerializer(secret_key)
        return self.serializer
    
    def send_verification_email(self, email, token_or_type):
        """
        Send verification email to user
        
        Args:
            email: User's email address
            token_or_type: Either a token string or "email_verification" type
        
        Returns:
            str: Generated token
        """
        try:
            # Generate token if not provided
            if token_or_type == "email_verification":
                serializer = self._get_serializer()
                token = serializer.dumps(email, salt='email-verification')
            else:
                token = token_or_type
            
            # Build verification URL
            base_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
            backend_url = os.environ.get('BACKEND_URL', 'http://localhost:5000')
            verification_url = f"{backend_url}/api/auth/confirm_email/{token}"
            
            # Create email message
            msg = Message(
                subject='Verify Your Matcha Account',
                recipients=[email],
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@matcha.com')
            )
            
            # Email body
            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .button {{ 
                        display: inline-block; 
                        padding: 12px 30px; 
                        background-color: #e91e63; 
                        color: white; 
                        text-decoration: none; 
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Welcome to Matcha! 💕</h1>
                    <p>Thank you for registering with Matcha. Please verify your email address to complete your registration.</p>
                    <p>Click the button below to verify your email:</p>
                    <a href="{verification_url}" class="button">Verify Email Address</a>
                    <p>Or copy and paste this link into your browser:</p>
                    <p><a href="{verification_url}">{verification_url}</a></p>
                    <p>This link will expire in 24 hours for security reasons.</p>
                    <div class="footer">
                        <p>If you didn't create an account with Matcha, please ignore this email.</p>
                        <p>&copy; 2025 Matcha. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.body = f"""
            Welcome to Matcha!
            
            Thank you for registering. Please verify your email address by clicking the link below:
            
            {verification_url}
            
            This link will expire in 24 hours.
            
            If you didn't create an account with Matcha, please ignore this email.
            
            © 2025 Matcha. All rights reserved.
            """
            
            # Send email
            mail = self._get_mail_instance()
            mail.send(msg)
            
            logger.info(f"✅ Verification email sent to {email}")
            return token
            
        except Exception as e:
            logger.error(f"❌ Failed to send verification email to {email}: {str(e)}")
            raise Exception(f"Failed to send verification email: {str(e)}")
    
    def send_password_reset_email(self, email, token):
        """
        Send password reset email
        
        Args:
            email: User's email address
            token: Password reset token
        
        Returns:
            bool: True if sent successfully
        """
        try:
            # Build reset URL
            base_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
            reset_url = f"{base_url}/reset-password/{token}"
            
            # Create email message
            msg = Message(
                subject='Reset Your Matcha Password',
                recipients=[email],
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@matcha.com')
            )
            
            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .button {{ 
                        display: inline-block; 
                        padding: 12px 30px; 
                        background-color: #e91e63; 
                        color: white; 
                        text-decoration: none; 
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Password Reset Request</h1>
                    <p>We received a request to reset your password for your Matcha account.</p>
                    <p>Click the button below to reset your password:</p>
                    <a href="{reset_url}" class="button">Reset Password</a>
                    <p>Or copy and paste this link into your browser:</p>
                    <p><a href="{reset_url}">{reset_url}</a></p>
                    <p>This link will expire in 1 hour for security reasons.</p>
                    <div class="footer">
                        <p>If you didn't request a password reset, please ignore this email or contact support if you have concerns.</p>
                        <p>&copy; 2025 Matcha. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.body = f"""
            Password Reset Request
            
            We received a request to reset your password. Click the link below to reset it:
            
            {reset_url}
            
            This link will expire in 1 hour.
            
            If you didn't request this, please ignore this email.
            
            © 2025 Matcha. All rights reserved.
            """
            
            # Send email
            mail = self._get_mail_instance()
            mail.send(msg)
            
            logger.info(f"✅ Password reset email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send password reset email to {email}: {str(e)}")
            raise Exception(f"Failed to send password reset email: {str(e)}")
    
    def confirm_email(self, token, max_age=86400):
        """
        Verify email confirmation token
        
        Args:
            token: Token to verify
            max_age: Maximum age in seconds (default 24 hours)
        
        Returns:
            str: Email address if valid
        
        Raises:
            SignatureExpired: If token has expired
            BadSignature: If token is invalid
        """
        try:
            serializer = self._get_serializer()
            email = serializer.loads(
                token,
                salt='email-verification',
                max_age=max_age
            )
            return email
        except SignatureExpired:
            logger.warning(f"Token expired for confirmation")
            raise SignatureExpired("Verification link has expired")
        except BadSignature:
            logger.warning(f"Invalid token for confirmation")
            raise BadSignature("Invalid verification link")
        except Exception as e:
            logger.error(f"Error confirming email: {str(e)}")
            raise
    
    def send_notification_email(self, email, subject, message):
        """
        Send a general notification email
        
        Args:
            email: Recipient email
            subject: Email subject
            message: Email message
        
        Returns:
            bool: True if sent successfully
        """
        try:
            msg = Message(
                subject=subject,
                recipients=[email],
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@matcha.com'),
                body=message
            )
            
            mail = self._get_mail_instance()
            mail.send(msg)
            
            logger.info(f"✅ Notification email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send notification email to {email}: {str(e)}")
            return False

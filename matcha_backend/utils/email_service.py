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
            backend_url = os.environ.get('BACKEND_URL') or current_app.config.get('BACKEND_URL') or 'http://localhost:5000'
            verification_url = f"{backend_url}/api/auth/confirm_email/{token}"
            
            # Check if email configuration is present FIRST
            mail_username = current_app.config.get('MAIL_USERNAME') or os.environ.get('MAIL_USERNAME')
            mail_password = current_app.config.get('MAIL_PASSWORD') or os.environ.get('MAIL_PASSWORD')
            smtp_key = os.environ.get('SMTP_SECRET_KEY')
            
            # Use the app password from SMTP_SECRET_KEY if MAIL_PASSWORD is not set
            if not mail_password and smtp_key:
                mail_password = smtp_key
            
            # Check if using console email mode (for development)
            use_console = os.environ.get('MAIL_USE_CONSOLE', 'false').lower() == 'true'
            
            # If no credentials and not explicitly console mode, enable console mode with warning
            if (not mail_username or not mail_password) and not use_console:
                logger.warning("⚠️  No SMTP credentials found - automatically using CONSOLE MODE")
                use_console = True
            
            if use_console:
                # Print email to console instead of sending
                logger.info("=" * 80)
                logger.info("📧 CONSOLE EMAIL MODE - Email would be sent to: %s", email)
                logger.info("=" * 80)
                logger.info("Subject: Verify Your Matcha Account")
                logger.info("From: noreply@matcha.com")
                logger.info("To: %s", email)
                logger.info("-" * 80)
                logger.info("Welcome to Matcha! 💕")
                logger.info("")
                logger.info("Thank you for registering. Please verify your email address.")
                logger.info("")
                logger.info("Verification Link:")
                logger.info("👉 %s", verification_url)
                logger.info("")
                logger.info("This link will expire in 24 hours.")
                logger.info("=" * 80)
                return token
            
            # Validate we have credentials for SMTP mode
            if not mail_username or not mail_password:
                error_msg = (
                    "❌ Email configuration missing!\n"
                    "\n"
                    "MAIL_USERNAME or MAIL_PASSWORD not set.\n"
                    "\n"
                    "Solutions:\n"
                    "1. Set environment variables with Gmail credentials:\n"
                    "   export MAIL_USERNAME='your-email@gmail.com'\n"
                    "   export MAIL_PASSWORD='your-app-password'\n"
                    "\n"
                    "2. Use console mode for testing (no SMTP needed):\n"
                    "   export MAIL_USE_CONSOLE='true'\n"
                    "\n"
                    "3. See EMAIL_SETUP_GUIDE.md or YOPMAIL_TESTING_GUIDE.md\n"
                    "\n"
                    "⚠️  Note: YOPmail cannot be used as MAIL_USERNAME!\n"
                    "   YOPmail is for RECEIVING only. Use Gmail to SEND.\n"
                )
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Create email message
            sender_addr = (
                current_app.config.get('MAIL_DEFAULT_SENDER')
                or current_app.config.get('MAIL_USERNAME')
                or os.environ.get('MAIL_USERNAME')
                or 'noreply@matcha.com'
            )
            msg = Message(
                subject='Verify Your Matcha Account',
                recipients=[email],
                sender=sender_addr,
            )
            
            # Email body with beautiful button (inline styles for better email client compatibility)
            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 40px 20px;">
                    <tr>
                        <td align="center">
                            <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <!-- Header -->
                                <tr>
                                    <td style="background: linear-gradient(135deg, #e91e63 0%, #f06292 100%); background-color: #e91e63; padding: 40px 20px; text-align: center; color: white;">
                                        <div style="font-size: 48px; margin-bottom: 10px;">💕</div>
                                        <h1 style="margin: 0; font-size: 32px; font-weight: 600; color: white;">Welcome to Matcha!</h1>
                                    </td>
                                </tr>
                                
                                <!-- Content -->
                                <tr>
                                    <td style="padding: 40px 30px; text-align: center;">
                                        <p style="font-size: 18px; font-weight: 500; color: #333; margin: 15px 0;">Thank you for joining Matcha!</p>
                                        <p style="font-size: 16px; color: #555; margin: 15px 0;">We're excited to have you here. To complete your registration and start connecting with amazing people, please verify your email address.</p>
                                        
                                        <!-- Button -->
                                        <table width="100%" cellpadding="0" cellspacing="0" style="margin: 35px 0;">
                                            <tr>
                                                <td align="center">
                                                    <a href="{verification_url}" style="display: inline-block; padding: 16px 40px; background: linear-gradient(135deg, #e91e63 0%, #f06292 100%); background-color: #e91e63; color: #ffffff; text-decoration: none; border-radius: 50px; font-size: 18px; font-weight: 600; box-shadow: 0 4px 15px rgba(233, 30, 99, 0.4);">✓ Verify Email Address</a>
                                                </td>
                                            </tr>
                                        </table>
                                        
                                        <p style="color: #999; font-size: 14px; margin: 15px 0;">This verification link will expire in 24 hours for security reasons.</p>
                                        
                                        <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
                                        
                                        <div style="font-size: 13px; color: #999; word-break: break-all;">
                                            <p style="margin: 10px 0;">If the button doesn't work, copy and paste this link into your browser:</p>
                                            <p style="margin: 10px 0;"><a href="{verification_url}" style="color: #e91e63; text-decoration: none;">{verification_url}</a></p>
                                        </div>
                                    </td>
                                </tr>
                                
                                <!-- Footer -->
                                <tr>
                                    <td style="background-color: #fafafa; padding: 25px 30px; text-align: center; font-size: 13px; color: #999; border-top: 1px solid #e0e0e0;">
                                        <p style="margin: 5px 0;">If you didn't create an account with Matcha, please ignore this email.</p>
                                        <p style="margin: 5px 0;">&copy; 2025 Matcha. All rights reserved.</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
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
            
            # Send email with timeout protection
            try:
                mail = self._get_mail_instance()
                with current_app.app_context():
                    # Use gevent timeout to prevent hanging
                    import gevent
                    from gevent import Timeout
                    
                    timeout = Timeout(15)  # 15 second timeout
                    timeout.start()
                    try:
                        mail.send(msg)
                        logger.info(f"✅ Verification email sent to {email}")
                    finally:
                        timeout.close()
                        
            except Timeout:
                logger.error(f"❌ SMTP timeout for {email} - Gmail SMTP not responding")
                raise Exception(f"Email server timeout. Gmail SMTP may be blocked or slow. Please try again.")
            except Exception as send_error:
                error_msg = str(send_error).lower()
                logger.error(f"❌ SMTP send error for {email}: {str(send_error)}")
                
                # Provide helpful error messages
                if "timeout" in error_msg or "timed out" in error_msg:
                    raise Exception(f"Email server timeout. Please try again later.")
                elif "authentication" in error_msg or "username" in error_msg or "password" in error_msg:
                    raise Exception(f"Gmail authentication failed. Please check email credentials.")
                elif "connection" in error_msg or "refused" in error_msg:
                    raise Exception(f"Cannot connect to Gmail SMTP. Check network or firewall.")
                else:
                    raise Exception(f"Failed to send email: {str(send_error)}")
            
            return token
            
        except Exception as e:
            logger.error(f"❌ Failed to send verification email to {email}: {str(e)}")
            raise Exception(f"Failed to send verification email: {str(e)}")
    
    def send_password_reset_email(self, email, username):
        """
        Send password reset email
        
        Args:
            email: User's email address
            username: Username for the reset token
        
        Returns:
            str: Generated reset token
        """
        try:
            # Generate token using serializer (same as email verification)
            serializer = self._get_serializer()
            token = serializer.dumps(email, salt='password-reset')
            
            # Build reset URL - points to BACKEND endpoint that will redirect to frontend with username
            backend_url = os.environ.get('BACKEND_URL', 'http://localhost:5000')
            reset_url = f"{backend_url}/api/auth/confirm_email_reset/{token}"
            
            # Check if using console email mode (for development)
            use_console = os.environ.get('MAIL_USE_CONSOLE', 'false').lower() == 'true'
            
            if use_console:
                # Print email to console instead of sending
                logger.info("=" * 80)
                logger.info("📧 CONSOLE EMAIL MODE - Password reset email would be sent to: %s", email)
                logger.info("=" * 80)
                logger.info("Subject: Reset Your Matcha Password")
                logger.info("From: noreply@matcha.com")
                logger.info("To: %s", email)
                logger.info("-" * 80)
                logger.info("Password Reset Request")
                logger.info("")
                logger.info("We received a request to reset your password.")
                logger.info("")
                logger.info("Reset Link:")
                logger.info("👉 %s", reset_url)
                logger.info("")
                logger.info("This link will expire in 1 hour.")
                logger.info("=" * 80)
                return token
            
            # Create email message with beautiful styling matching verification email
            sender_addr = (
                current_app.config.get('MAIL_DEFAULT_SENDER')
                or current_app.config.get('MAIL_USERNAME')
                or os.environ.get('MAIL_USERNAME')
                or 'noreply@matcha.com'
            )
            msg = Message(
                subject='Reset Your Matcha Password',
                recipients=[email],
                sender=sender_addr
            )
            
            # Beautiful HTML email with button (matching verification email style)
            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 40px 20px;">
                    <tr>
                        <td align="center">
                            <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                <!-- Header -->
                                <tr>
                                    <td style="background: linear-gradient(135deg, #e91e63 0%, #f06292 100%); background-color: #e91e63; padding: 40px 20px; text-align: center; color: white;">
                                        <div style="font-size: 48px; margin-bottom: 10px;">🔒</div>
                                        <h1 style="margin: 0; font-size: 32px; font-weight: 600; color: white;">Forgot your password?</h1>
                                    </td>
                                </tr>
                                
                                <!-- Content -->
                                <tr>
                                    <td style="padding: 40px 30px; text-align: center;">
                                        <p style="font-size: 16px; color: #555; margin: 15px 0;">No worries! Enter your username and we'll send you instructions to reset your password.</p>
                                        <p style="font-size: 16px; color: #555; margin: 15px 0;">If an account exists for that username, we sent a password reset link to your email. Please check your inbox and click the link to reset your password.</p>
                                        
                                        <!-- Button -->
                                        <table width="100%" cellpadding="0" cellspacing="0" style="margin: 35px 0;">
                                            <tr>
                                                <td align="center">
                                                    <a href="{reset_url}" style="display: inline-block; padding: 16px 40px; background: linear-gradient(135deg, #e91e63 0%, #f06292 100%); background-color: #e91e63; color: #ffffff; text-decoration: none; border-radius: 50px; font-size: 18px; font-weight: 600; box-shadow: 0 4px 15px rgba(233, 30, 99, 0.4);">🔑 Reset Password</a>
                                                </td>
                                            </tr>
                                        </table>
                                        
                                        <p style="color: #999; font-size: 14px; margin: 15px 0;">This verification link will expire in 24 hours for security reasons.</p>
                                        
                                        <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
                                        
                                        <div style="font-size: 13px; color: #999; word-break: break-all;">
                                            <p style="margin: 10px 0;">If the button doesn't work, copy and paste this link into your browser:</p>
                                            <p style="margin: 10px 0;"><a href="{reset_url}" style="color: #e91e63; text-decoration: none;">{reset_url}</a></p>
                                        </div>
                                    </td>
                                </tr>
                                
                                <!-- Footer -->
                                <tr>
                                    <td style="background-color: #fafafa; padding: 25px 30px; text-align: center; font-size: 13px; color: #999; border-top: 1px solid #e0e0e0;">
                                        <p style="margin: 5px 0;">If you didn't request a password reset, please ignore this email or contact support if you have concerns.</p>
                                        <p style="margin: 5px 0;">&copy; 2025 Matcha. All rights reserved.</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """
            
            msg.body = f"""
            Forgot your password?
            
            No worries! We received a request to reset your password for your Matcha account.
            
            Click the link below to reset your password:
            
            {reset_url}
            
            This link will expire in 24 hours for security reasons.
            
            If you didn't request a password reset, please ignore this email.
            
            © 2025 Matcha. All rights reserved.
            """
            
            # Send email with timeout protection
            try:
                mail = self._get_mail_instance()
                with current_app.app_context():
                    # Use gevent timeout to prevent hanging
                    import gevent
                    from gevent import Timeout
                    
                    timeout = Timeout(15)  # 15 second timeout
                    timeout.start()
                    try:
                        mail.send(msg)
                        logger.info(f"✅ Password reset email sent to {email}")
                    finally:
                        timeout.close()
                        
            except Timeout:
                logger.error(f"❌ SMTP timeout for {email} - Gmail SMTP not responding")
                raise Exception(f"Email server timeout. Please try again.")
            except Exception as send_error:
                error_msg = str(send_error).lower()
                logger.error(f"❌ SMTP send error for {email}: {str(send_error)}")
                
                if "timeout" in error_msg or "timed out" in error_msg:
                    raise Exception(f"Email server timeout. Please try again later.")
                elif "authentication" in error_msg or "username" in error_msg or "password" in error_msg:
                    raise Exception(f"Gmail authentication failed. Please check email credentials.")
                elif "connection" in error_msg or "refused" in error_msg:
                    raise Exception(f"Cannot connect to Gmail SMTP. Check network or firewall.")
                else:
                    raise Exception(f"Failed to send email: {str(send_error)}")
            
            return token
            
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
    
    def confirm_reset_token(self, token, max_age=3600):
        """
        Verify password reset token
        
        Args:
            token: Token to verify
            max_age: Maximum age in seconds (default 1 hour)
        
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
                salt='password-reset',
                max_age=max_age
            )
            return email
        except SignatureExpired:
            logger.warning(f"Password reset token expired")
            raise SignatureExpired("Password reset link has expired")
        except BadSignature:
            logger.warning(f"Invalid password reset token")
            raise BadSignature("Invalid password reset link")
        except Exception as e:
            logger.error(f"Error confirming reset token: {str(e)}")
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

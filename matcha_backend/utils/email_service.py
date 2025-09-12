from flask_mail import Mail, Message
from flask import url_for, current_app
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask import current_app, jsonify
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class EmailService:
    def __init__(self, app=None):
        self.app = app or current_app
        self.mail = self.app.extensions.get('mail')
        
        if not self.mail:
            logger.warning("Mail extension not found - emails will not be sent")
            self.mail = None
            return

        self.secret_key = self.app.config["SMTP_SECRET_KEY"]
        self.serializer = URLSafeTimedSerializer(self.secret_key)

    def send_verification_email(self, email, verification_type):
        if verification_type not in ["reset_password", "email_verification"]:
            raise Exception("Verification type not specified")
        token = self.serializer.dumps(email, salt='email-confirm')
        logger.info(f"✅ Generated verification token for {email}")
        
        # If mail is not configured or in debug mode, skip sending
        if not self.mail:
            logger.warning(f"Email not sent to {email} (debug mode or mail not configured)")
            return token
            
        try:
            route = 'auth.confirm_email'\
                if verification_type == "email_verification"\
                    else "auth.confirm_email_reset"
            smtp_config = self.app.config.get('smtp', {})
            sender_email = smtp_config.get("MAIL_USERNAME")
            
            msg = Message('Confirm Email', sender=sender_email, recipients=[email])
            link = url_for(
                route,
                token=token,
                _external=True)
            msg.body = 'Your link is {}'.format(link)
            msg.html = f'''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">Email Verification</h2>
            <p>Please verify your email address by clicking the button below:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{link}" 
                   style="background-color: #4CAF50; color: white; padding: 15px 30px; 
                          text-decoration: none; border-radius: 5px; font-size: 16px;">
                   Verify Email Address
                </a>
            </div>
            
            <p>Or copy and paste this link in your browser:</p>
            <p style="word-break: break-all; color: #666; background-color: #f9f9f9; 
                      padding: 10px; border-radius: 4px;">
                {link}
            </p>
            
            <p>If you did not create an account, please ignore this email.</p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="color: #999; font-size: 12px;">
                Thank you,<br>
                The Matcha Team
            </p>
        </div>
        '''
            self.mail.send(msg)
            logger.info(f"✅ Verification email sent to {email}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {email}: {e}")
            # Don't raise the error - still return the token for database storage
            # The user can request a new email later if needed
            
        return token

    def confirm_email(self, token):
        try:
            logger.info(f"✅✅✅✅✅✅✅✅✅✅✅")
            email = self.serializer.loads(token, salt='email-confirm', max_age=3600)
            return email
        except SignatureExpired:
            raise SignatureExpired("The verification link has expired.")
        except Exception as e:
            raise ValueError("Invalid verification token.")

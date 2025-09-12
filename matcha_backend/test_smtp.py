import smtplib
import ssl
import os

def test_gmail_connection():
    try:
        # Get your credentials from environment variables
        email = "matcha.42.1337.42@gmail.com" # Your full Gmail address
        password = "ngwk dzex gurv vuur "  # Your 16-character app password
        
        
        print(f"Testing connection to Gmail with: {email}")
        print(f"Password length: {len(password) if password else 0} characters")
        
        # Try SSL first (port 465)
        print("Trying SSL (port 465)...")
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(email, password)
            print("✅ Successfully connected with SSL!")
            return True
            
    except Exception as e:
        print(f"❌ SSL failed: {e}")
        
        # Try TLS (port 587)
        try:
            print("Trying TLS (port 587)...")
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(email, password)
                print("✅ Successfully connected with TLS!")
                return True
        except Exception as e2:
            print(f"❌ TLS also failed: {e2}")
            return False

# Run the test
test_gmail_connection()
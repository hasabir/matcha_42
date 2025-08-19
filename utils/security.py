from flask import current_app


class SecurityUtils:
    def password_hash(password):
        """Hash a password using the configured bcrypt instance."""
        bcrypt = current_app.config.get('BCRYPT')
        if not bcrypt:
            raise RuntimeError("BCRYPT not configured in app context")
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
    def password_check(hashed_password, password): #! or should i fetch user form db?
        """Check a password against a hashed password."""
        bcrypt = current_app.config.get('BCRYPT')
        if not bcrypt:
            raise RuntimeError("BCRYPT not configured in app context")
        return bcrypt.check_password_hash(hashed_password, password)